import numpy as np, trimesh, cv2, json
from pathlib import Path
from PIL import Image, ImageDraw
P=Path('/mnt/data')
MASK=P/'forge_artwork_ai_results'
scenes={
    'V15':trimesh.load(P/'FORGE_V15_ReferenceRebuild.glb',force='scene',process=False),
    'V16':trimesh.load(P/'FORGE_V16_ReferenceFit.glb',force='scene',process=False),
}

def projection(scene,view,shape):
    H,W=shape;out=np.zeros((H,W),np.uint8)
    for node in scene.graph.nodes_geometry:
        t,geo=scene.graph.get(node)
        mesh=scene.geometry[geo]
        v=mesh.vertices@t[:3,:3].T+t[:3,3]
        if view=='left_side':
            x=29+(3.90-v[:,2])*78.6; y=163-(v[:,1]-.065)*78.6
        elif view=='top':
            x=145+v[:,0]*58.6; y=7+(3.9-v[:,2])*58.6
        elif view in ('front','rear'):
            x=(W/2)+v[:,0]*64.7;y=164-(v[:,1]-.065)*64.7
        uv=np.stack([x,y],axis=-1)
        for f in mesh.faces:
            pts=np.rint(uv[f]).astype(np.int32)
            cv2.fillConvexPoly(out,pts,255)
    return out>127

def score(ref,pred):
    tp=int(np.logical_and(ref,pred).sum());fp=int(np.logical_and(~ref,pred).sum());fn=int(np.logical_and(ref,~pred).sum())
    p=tp/max(tp+fp,1);r=tp/max(tp+fn,1)
    return {'iou':round(tp/max(tp+fp+fn,1),5),
            'precision':round(p,5),'recall':round(r,5),
            'f2':round(5*p*r/max(4*p+r,1e-12),5),
            'missing':fn,'extra':fp}

results={}
for view in ['left_side','top','front','rear']:
    ref=np.array(Image.open(MASK/(view+'_auto_mask.png')).convert('L'))>=128
    results[view]={}
    panes=[]
    image=Image.open(P/'forge_v16_work/original_reference/FORGE_8view.jpg') if False else None
    for version,scene in scenes.items():
        rendered=projection(scene,view,ref.shape)
        results[view][version]=score(ref,rendered)
        overlay=np.zeros((*ref.shape,3),dtype=np.uint8)
        overlay[ref & rendered] = (202,207,207)
        overlay[ref & ~rendered] = (244,82,76)
        overlay[~ref & rendered] = (70,194,233)
        panes.append(Image.fromarray(overlay))
    W,H=panes[0].size
    comparison=Image.new('RGB',(W*2,H+34),(25,29,35))
    draw=ImageDraw.Draw(comparison)
    for i,k in enumerate(scenes):
        comparison.paste(panes[i],(i*W,34))
        d=results[view][k]
        draw.text((i*W+8,8),f'{k} IoU {d["iou"]:.3f}  recall {d["recall"]:.3f}  F2 {d["f2"]:.3f}',fill='white')
    comparison.save(P/f'FORGE_V16_{view}_SILHOUETTE.png')
    print(view,results[view])
for version in scenes:
    avg={k:float(np.mean([results[v][version][k] for v in ['left_side','top','front','rear']])) for k in ['iou','recall','precision','f2']}
    print('MEAN',version,avg)
    results[version+'_average']=avg
(P/'FORGE_V16_COMPARISON_REPORT.json').write_text(json.dumps({'method':'Fixed manually calibrated 4-view orthographic silhouette projections, GrabCut-based masks (approximately orthographic source art); qualitative AI features, not ground truth measurements', 'results':results},indent=2)+'\n')

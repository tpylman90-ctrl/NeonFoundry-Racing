using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

/// <summary>Builds the first Neon Foundry Unity Android vertical slice from Blender meshes.</summary>
public static class NeonFoundryUnityBuild
{
    private const string ScenePath = "Assets/Scenes/FoundryGarage.unity";
    private const string CraftPath = "Assets/Resources/Foundry/ForgeReviewCraft.obj";
    private const string GaragePath = "Assets/Resources/Foundry/FoundryGarage.obj";
    private const string RendererPath = "Assets/Settings/FoundryRenderer.asset";
    private const string PipelinePath = "Assets/Settings/FoundryURP.asset";
    private const string MaterialsPath = "Assets/Settings/FoundryMaterials";
    private const string ApkPath = "Builds/Android/NeonFoundry-Unity-Garage.apk";

    [MenuItem("Neon Foundry/Build Garage Inspection Scene")]
    public static void PrepareScene()
    {
        EnsureFolder("Assets/Scenes");
        EnsureFolder("Assets/Settings");
        EnsureFolder(MaterialsPath);
        Require(CraftPath);
        Require(GaragePath);

        UniversalRendererData renderer = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(RendererPath);
        if (renderer == null)
        {
            renderer = ScriptableObject.CreateInstance<UniversalRendererData>();
            AssetDatabase.CreateAsset(renderer, RendererPath);
        }
        UniversalRenderPipelineAsset pipeline =
            AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(PipelinePath);
        if (pipeline == null)
        {
            pipeline = UniversalRenderPipelineAsset.Create(renderer);
            AssetDatabase.CreateAsset(pipeline, PipelinePath);
        }
        pipeline.renderScale = .90f;
        pipeline.supportsHDR = true;
        pipeline.msaaSampleCount = 2;
        pipeline.shadowDistance = 36f;
        GraphicsSettings.defaultRenderPipeline = pipeline;
        QualitySettings.renderPipeline = pipeline;
        EditorUtility.SetDirty(pipeline);

        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        SetupEnvironment();
        GameObject garage = Instantiate( GaragePath, "Blender | Foundry garage environment");
        GameObject craft = Instantiate( CraftPath, "Blender | FORGE craft review geometry");
        garage.transform.position = Vector3.zero;
        craft.transform.position = new Vector3(0f, 0.28f, 0f);
        ApplyMaterials(garage);
        ApplyMaterials(craft);
        SetupWalkableSurfaces();

        var craftFocus = new GameObject("Target | Craft");
        craftFocus.transform.position = new Vector3(0, 1.4f, 0);
        var batteryFocus = new GameObject("Target | Battery works");
        batteryFocus.transform.position = new Vector3(-4.2f, 2.2f, -12.2f);
        var deckFocus = new GameObject("Target | Observation deck");
        deckFocus.transform.position = new Vector3(11.8f, 3.5f, -12.5f);

        var cameraObject = new GameObject("Main Camera | Touch inspection");
        cameraObject.tag = "MainCamera";
        var camera = cameraObject.AddComponent<Camera>();
        camera.fieldOfView = 55f;
        camera.nearClipPlane = .06f;
        camera.farClipPlane = 125f;
        camera.allowHDR = true;
        cameraObject.AddComponent<AudioListener>();
        var cameraData = cameraObject.AddComponent<UniversalAdditionalCameraData>();
        cameraData.renderPostProcessing = true;
        cameraObject.AddComponent<FoundryGarageViewer>()
            .Initialize(craftFocus.transform,batteryFocus.transform,deckFocus.transform);

        SetupLocalLighting();
        SetupPostProcessing();
        EditorBuildSettings.scenes = new [] { new EditorBuildSettingsScene(ScenePath,true) };
        if (!EditorSceneManager.SaveScene(scene,ScenePath))
            throw new Exception("Could not save Foundry Unity preview scene");
        AssetDatabase.SaveAssets();
        Debug.Log("NEON_FOUNDRY_UNITY_SCENE_OK");
    }
    private static GameObject Instantiate(string path,string name)
    {
        GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
        if (model == null) throw new Exception("Failed Blender OBJ import: "+path);
        GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(model);
        instance.name = name;
        return instance;
    }
    private static void Require(string path)
    {
        if (!File.Exists(path)) throw new Exception("Missing Blender mesh "+path);
        AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceUpdate);
    }
    private static Material EnsureMaterial(string key,Color color,float metallic,float smoothness,
        float emission=0f)
    {
        string path = MaterialsPath + "/" + key + ".mat";
        Material m=AssetDatabase.LoadAssetAtPath<Material>(path);
        if(m == null)
        {
            Shader shader=Shader.Find("Universal Render Pipeline/Lit");
            if(shader==null) throw new Exception("URP Lit shader unavailable");
            m=new Material(shader) { name=key };
            AssetDatabase.CreateAsset(m,path);
        }
        m.SetColor("_BaseColor",color);
        m.SetFloat("_Metallic",metallic);
        m.SetFloat("_Smoothness",smoothness);
        if(emission>0f)
        {
            m.SetColor("_EmissionColor",color*emission);
            m.EnableKeyword("_EMISSION");
        }
        m.enableInstancing = true;
        EditorUtility.SetDirty(m);
        return m;
    }
    private static void ApplyMaterials(GameObject root)
    {
        var armor=EnsureMaterial("NF_ARMOR",new Color(.29f,.37f,.44f),.70f,.71f);
        var carbon=EnsureMaterial("NF_CARBON",new Color(.014f,.023f,.035f),.20f,.48f);
        var steel=EnsureMaterial("NF_STEEL",new Color(.57f,.61f,.65f),.78f,.64f);
        var glass=EnsureMaterial("NF_GLASS",new Color(.018f,.125f,.20f),.48f,.89f);
        var cyan=EnsureMaterial("NF_CYAN",new Color(.012f,.60f,.94f),.10f,.58f,2.4f);
        var amber=EnsureMaterial("NF_AMBER",new Color(1f,.23f,.028f),.12f,.49f,1.9f);
        var floor=EnsureMaterial("NF_FLOOR",new Color(.14f,.155f,.17f),.28f,.31f);
        var wall=EnsureMaterial("NF_WALL",new Color(.18f,.20f,.225f),.42f,.47f);
        var rubber=EnsureMaterial("NF_RUBBER",new Color(.035f,.043f,.046f),.02f,.13f);
        var battery=EnsureMaterial("NF_BATTERY",new Color(.23f,.38f,.28f),.34f,.62f);
        var red=EnsureMaterial("NF_RED",new Color(.72f,.062f,.045f),.44f,.68f);
        ApplyBakedAlbedo(armor,"NF_ARMOR_COATED", new Vector2(2f,2f));
        ApplyBakedAlbedo(carbon,"NF_CARBON_WEAVE", new Vector2(3f,3f));
        ApplyBakedAlbedo(steel,"NF_STEEL_BRUSHED", new Vector2(2f,2f));
        ApplyBakedAlbedo(floor,"NF_FLOOR_SURFACE", new Vector2(4f,4f));
        ApplyBakedAlbedo(wall,"NF_WALL_STAMPED", new Vector2(3f,3f));
        foreach (Renderer r in root.GetComponentsInChildren<Renderer>(true))
        {
            Material[] source=r.sharedMaterials;
            var mapped=new Material[source.Length];
            for(int i=0;i<source.Length;i++)
            {
                string n=source[i] == null ? "" : source[i].name.ToUpperInvariant();
                if(n.Contains("NF_CARBON"))mapped[i]=carbon;
                else if(n.Contains("NF_ARMOR"))mapped[i]=armor;
                else if(n.Contains("NF_STEEL"))mapped[i]=steel;
                else if(n.Contains("NF_GLASS"))mapped[i]=glass;
                else if(n.Contains("NF_CYAN"))mapped[i]=cyan;
                else if(n.Contains("NF_AMBER"))mapped[i]=amber;
                else if(n.Contains("NF_FLOOR"))mapped[i]=floor;
                else if(n.Contains("NF_WALL"))mapped[i]=wall;
                else if(n.Contains("NF_RUBBER"))mapped[i]=rubber;
                else if(n.Contains("NF_BATTERY"))mapped[i]=battery;
                else if(n.Contains("NF_RED"))mapped[i]=red;
                else mapped[i]=armor; // conspicuous fallback, never invisible
            }
            r.sharedMaterials=mapped;
            r.shadowCastingMode=ShadowCastingMode.On;
            r.receiveShadows=true;
        }
    }
    private static void ApplyBakedAlbedo(Material mat, string textureName, Vector2 tiling)
    {
        string path = "Assets/Resources/Foundry/Textures/" + textureName + ".png";
        if (!File.Exists(path))
            throw new Exception("Missing baked detail map: " + path);
        AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceUpdate);
        Texture2D tex = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        if (tex == null)
            throw new Exception("Failed to import baked detail map: " + path);
        mat.SetTexture("_BaseMap", tex);
        mat.SetTextureScale("_BaseMap", tiling);
        EditorUtility.SetDirty(mat);
    }
    /// <summary>Lightweight walkable proxy geometry, without attaching expensive
    /// collision meshes to the detailed batched 3D environment.</summary>
    private static void SetupWalkableSurfaces()
    {
        var root = new GameObject("Walkable | collision proxies");
        AddWalkBox(root.transform, "Garage floor", new Vector3(0,-.22f,0),
            new Vector3(35,.32f,37));
        AddWalkBox(root.transform, "Observation deck", new Vector3(11.8f,3.45f,-12.5f),
            new Vector3(8.1f,.25f,6.55f));
        for(int i=0;i<18;i++)
            AddWalkBox(root.transform, "Access stair " + (i+1),
                new Vector3(10.85f,.12f+i*.184f,-(2.55f+i*.53f)),
                new Vector3(2f,.16f,.51f));
    }
    private static void AddWalkBox(Transform root, string label, Vector3 center, Vector3 dimensions)
    {
        var obj = new GameObject(label);
        obj.transform.SetParent(root,false);
        obj.transform.position = center;
        var collider = obj.AddComponent<BoxCollider>();
        collider.size = dimensions;
    }
    private static void SetupEnvironment()
    {
        RenderSettings.ambientMode=AmbientMode.Trilight;
        RenderSettings.ambientSkyColor=new Color(.20f,.28f,.35f);
        RenderSettings.ambientEquatorColor=new Color(.13f,.18f,.22f);
        RenderSettings.ambientGroundColor=new Color(.05f,.065f,.075f);
        RenderSettings.ambientIntensity=.77f;
        RenderSettings.fog=true;
        RenderSettings.fogMode=FogMode.Linear;
        RenderSettings.fogColor=new Color(.08f,.12f,.17f);
        RenderSettings.fogStartDistance=38f;
        RenderSettings.fogEndDistance=110f;
        var sunObject=new GameObject("Lighting | cool hangar top light");
        var sun=sunObject.AddComponent<Light>();
        sun.type=LightType.Directional;
        sun.color=new Color(.77f,.87f,1f);
        sun.intensity=1.35f;
        sun.shadows=LightShadows.Soft;
        sun.shadowStrength=.68f;
        sunObject.transform.rotation=Quaternion.Euler(46f,-32f,0f);
        RenderSettings.sun=sun;
        var skyShader=Shader.Find("Skybox/Procedural");
        if(skyShader!=null)
        {
            Material sky=new Material(skyShader);
            sky.SetColor("_SkyTint",new Color(.16f,.30f,.46f));
            sky.SetFloat("_Exposure",.42f);
            RenderSettings.skybox=sky;
        }
    }
    private static void SetupLocalLighting()
    {
        CreateLamp("White main bay industrial fill",new Vector3(0,6.25f,0),
            new Color(.74f,.86f,1f),6.3f,17f);
        CreateLamp("Warm diagnostic stations",new Vector3(-7,5.9f,-12),
            new Color(1f,.58f,.29f),5.5f,13f);
        CreateLamp("Cool energy exchange",new Vector3(6,5.9f,-12),
            new Color(.28f,.70f,1f),4.1f,12f);
        CreateLamp("Dock door reflected daylight",new Vector3(0,5.6f,13),
            new Color(.69f,.81f,.96f),3.8f,12f);
    }
    private static void CreateLamp(string name,Vector3 position,Color color,float intensity,float range)
    {
        var obj=new GameObject("Lighting | "+name);
        obj.transform.position=position;
        var l=obj.AddComponent<Light>();
        l.type=LightType.Point;
        l.range=range;
        l.color=color;
        l.intensity=intensity;
        l.shadows=LightShadows.None; // Android avoids costly additional-light shadows
    }
    private static void SetupPostProcessing()
    {
        const string path="Assets/Settings/FoundryProfile.asset";
        VolumeProfile profile=AssetDatabase.LoadAssetAtPath<VolumeProfile>(path);
        if(profile==null)
        {
            profile=ScriptableObject.CreateInstance<VolumeProfile>();
            AssetDatabase.CreateAsset(profile,path);
        }
        Bloom bloom;
        if(!profile.TryGet(out bloom)) bloom=profile.Add<Bloom>(true);
        bloom.threshold.value=1.08f;
        bloom.intensity.value=.26f;
        bloom.scatter.value=.55f;
        ColorAdjustments grade;
        if(!profile.TryGet(out grade))grade=profile.Add<ColorAdjustments>(true);
        grade.contrast.value=14f;
        grade.saturation.value=-3f;
        Tonemapping tonemapping;
        if(!profile.TryGet(out tonemapping))tonemapping=profile.Add<Tonemapping>(true);
        tonemapping.mode.value=TonemappingMode.ACES;
        Vignette vignette;
        if(!profile.TryGet(out vignette))vignette=profile.Add<Vignette>(true);
        vignette.intensity.value=.12f;
        vignette.smoothness.value=.33f;
        var obj=new GameObject("Post | controlled emissive bloom");
        var volume=obj.AddComponent<Volume>();
        volume.isGlobal=true;
        volume.sharedProfile=profile;
        EditorUtility.SetDirty(profile);
    }
    private static void EnsureFolder(string path)
    {
        if(AssetDatabase.IsValidFolder(path)) return;
        string[] parts=path.Split('/');
        string parent=parts[0];
        for(int i=1;i<parts.Length;i++)
        {
            string child=parent+"/"+parts[i];
            if(!AssetDatabase.IsValidFolder(child))
                AssetDatabase.CreateFolder(parent,parts[i]);
            parent=child;
        }
    }
    public static void BuildAndroid()
    {
        PrepareScene();
        PlayerSettings.companyName="Neon Foundry";
        PlayerSettings.productName="Neon Foundry Garage Preview";
        PlayerSettings.bundleVersion="0.2.0";
        PlayerSettings.defaultInterfaceOrientation=UIOrientation.LandscapeLeft;
        PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android,
            "com.tpylman.neonfoundryracing.unityreview");
        PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android,ScriptingImplementation.IL2CPP);
        PlayerSettings.Android.targetArchitectures=AndroidArchitecture.ARM64;
        PlayerSettings.Android.minSdkVersion=AndroidSdkVersions.AndroidApiLevel26;
        PlayerSettings.Android.optimizedFramePacing=true;
        PlayerSettings.colorSpace=ColorSpace.Linear;
        PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android,false);
        PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,
            new[]{ GraphicsDeviceType.Vulkan, GraphicsDeviceType.OpenGLES3 });
        EditorUserBuildSettings.buildAppBundle=false;
        var projectRoot=Directory.GetParent(Application.dataPath).FullName;
        string apk=Path.GetFullPath(Path.Combine(projectRoot,ApkPath));
        Directory.CreateDirectory(Path.GetDirectoryName(apk));
        var result=BuildPipeline.BuildPlayer(new[]{ScenePath},apk,BuildTarget.Android,BuildOptions.None);
        if(result.summary.result != BuildResult.Succeeded)
            throw new Exception("Neon Foundry Android build failed: "+result.summary.result);
        if(!File.Exists(apk) || new FileInfo(apk).Length==0)
            throw new Exception("Missing or empty APK: "+apk);
        Debug.Log("NEON_FOUNDRY_UNITY_APK_OK "+apk);
    }
}

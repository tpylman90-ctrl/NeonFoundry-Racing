# FORGE donor-car experiment: two wheel-removal / hover conversions

**Status:** Experimental CC0 geometry study. Neither vehicle is the FORGE hero craft; neither is imported into the production garage. Source and game assets remain separate.

**Donor:** [Innerscene – Generic mid-engine supercar](https://www.innerscene.com/tools/library/3d-parts/generic-mid-engine-supercar-73f252c5), an original, unbranded model explicitly labeled **CC0** by its author. The downloadable GLB is 3,949,472 bytes, SHA-256 `ad0fd94845edb9af474407fe08fb379b624c56ec4d4b4ad6b47822b65c6f8903`. The source mesh has 348 objects and 104,282 triangles, including shaped coachwork, windows, 4 independent wheel assemblies, brake components, fender lips, interiors, vents and rear aero. No AI-generated or unlicensed Sketchfab geometry is substituted. Sketchfab Concept Car 037 (an alternative) currently displays a Free Standard license despite the creator's CC0 description; this experiment avoids that unresolved ambiguity.

## A. Externally mounted hover pods

`CC0_Supercar_VISIBLE_HOVER_PODS.glb` — Replaces **all four** conventional wheels, hubs, brake components, rims and tyre tread geometry with four physical modular hover cassettes, installed in the existing fender/wheelhouse openings. Each cassette includes a cradle, independent A-arms, tapered armored housing, segmented braces, a hollow annular metal emitter assembly, small gyro vanes and downward-directed luminous center. Wheelhouses and fender lips are retained intentionally to frame visible hover systems.

## B. No visible hubs / wheel-less coachwork

`CC0_Supercar_WHEELLESS_FLUSH_BODY.glb` — Deletes wheels, hubs, brakes, **and the wheelhouse liners and fender lips**. It bridges all four wheel openings with **separately modeled, double-curved, solid pressed-armor panels** matching the donor's paint color. Six independent vertical hover emitters are housed underneath with load brackets, concentric mechanical coils, shrouds and luminous centers. It is not simply a wheel hidden inside the old mesh.

**Important quality limitation:** The wheel-less arches currently use fitted, removable sculpted covers. Their panel boundaries are still visible and the covers are NOT topologically welded to the original body mesh. Achieving truly continuous Class-A exterior surfacing will require subsequent retopology of the body around those arches. This limitation should be assessed visually before upgrading or integrating into FORGE.

## Validation and legal provenance

The original authored sculpted body mesh, distinct panels, glass and materials remain as individual geometry; they are not recreated with blocks. The audited source has 348 objects. The pod variant removes 240 wheel subobjects and has ~61k triangles. The wheel-less variant removes 248 (including wheelhouses) and has ~60k triangles. Both are separate GLBs for Android GLB viewer and a visual comparison, not claimed to be fully optimized game models.

Reproduce:
```sh
mkdir -p build/donor
curl -L --fail -o build/donor/original_CC0_mid_engine_supercar.glb 'https://www.innerscene.com/api/library/generic-mid-engine-supercar-73f252c5/download'
python -m pip install numpy trimesh networkx scipy Pillow
python tools/build_cc0_donor_hover_variants.py --variant pods
python tools/build_cc0_donor_hover_variants.py --variant flush
```
`NFR_DONOR_SOURCE` and `NFR_DONOR_OUTPUT` override the input/output paths.

**Next experiment if approved:** select the better of these treatments and fit a customized donor panel system to the already-approved V18 wide/deep FORGE chassis (with proper reshaped wheel-well topology). Avoid importing the donor's original branding or claiming that the donor is original FORGE design.

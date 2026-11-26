using UnityEngine;
using System.Collections.Generic;

/// <summary>Android-first garage inspection and walkaround controls.
/// Preview deliberately preserves an accessible orbit mode before any racing physics.
/// </summary>
public sealed class FoundryGarageViewer : MonoBehaviour
{
    private Camera cam;
    [SerializeField] private Transform craftTarget, cellTarget, deckTarget, stationTarget;
    [SerializeField] private GameObject stationRoot;
    private readonly List<Renderer> guardPanels = new List<Renderer>();
    private bool guardsVisible = true;
    private Transform[] destinations;
    private string[] labels = { "CRAFT", "CELL WORKS", "OVERLOOK", "NF-BW01" };
    private int locationIndex;
    private Vector3 focus;
    private bool walkMode;
    private float yaw = -138f, pitch = 11f, orbitDistance = 12.9f;
    private Vector3 walker = new Vector3(0f, 1.75f, -10f);
    private float lookPitch = 8f, walkYaw = 0f;
    private Vector2 previousPointer;
    private float previousPinch;
    private Vector2 leftStick;
    private Vector2 stickOrigin;
    private int leftFinger = -1, rightFinger = -1;
    private float fpsTime, fps;
    private int frames;
    private GUIStyle headStyle, bodyStyle, buttonStyle, tinyStyle;
    private Texture2D darkButtonTexture;

    public void Initialize(Transform craft, Transform cellWorks, Transform overlook,
                           Transform station, GameObject machine)
    {
        craftTarget = craft;
        cellTarget = cellWorks;
        deckTarget = overlook;
        stationTarget = station;
        stationRoot = machine;
        destinations = new[] { craft, cellWorks, overlook, station };
        focus = craft.position;
        CacheGuardPanels();
    }
    private void CacheGuardPanels()
    {
        guardPanels.Clear();
        if (stationRoot == null) return;
        foreach(Renderer r in stationRoot.GetComponentsInChildren<Renderer>(true))
        {
            string n = r.gameObject.name.ToUpperInvariant();
            if (n.Contains("SLIDING TRANSPARENT GATE")
                || n.Contains("SAFETY GLAZING")
                || n.Contains("CLEAR GUARDING"))
                guardPanels.Add(r);
        }
    }
    private void ToggleGuarding()
    {
        guardsVisible = !guardsVisible;
        foreach(Renderer r in guardPanels)
            if (r != null) r.enabled = guardsVisible;
    }
    void Awake()
    {
        cam = GetComponent<Camera>();
        destinations = new[] { craftTarget, cellTarget, deckTarget, stationTarget };
        CacheGuardPanels();
        Application.targetFrameRate = 60;
        QualitySettings.vSyncCount = 0;
        fpsTime = Time.unscaledTime;
        if (craftTarget != null) focus = craftTarget.position;
        UpdateCamera();
    }
    void Update()
    {
        frames++;
        if (Time.unscaledTime - fpsTime >= .6f)
        {
            fps = frames / (Time.unscaledTime - fpsTime);
            frames = 0;
            fpsTime = Time.unscaledTime;
        }
        if (walkMode) UpdateWalk();
        else UpdateOrbit();
        UpdateCamera();
    }
    void UpdateOrbit()
    {
        if (Input.touchCount == 1)
        {
            Touch t = Input.GetTouch(0);
            if (t.phase == TouchPhase.Began) previousPointer = t.position;
            if (t.phase == TouchPhase.Moved && !OverTopButtons(t.position))
            {
                Vector2 delta = t.position - previousPointer;
                yaw += delta.x * .19f;
                pitch = Mathf.Clamp(pitch - delta.y * .15f, -12f, 80f);
                previousPointer = t.position;
            }
        }
        else if (Input.touchCount >= 2)
        {
            Touch a = Input.GetTouch(0), b = Input.GetTouch(1);
            float pinch = Vector2.Distance(a.position, b.position);
            if (a.phase == TouchPhase.Began || b.phase == TouchPhase.Began || previousPinch <= 0f)
                previousPinch = pinch;
            else
            {
                orbitDistance = Mathf.Clamp(orbitDistance - (pinch - previousPinch) * .028f, locationIndex==3?2.4f:5f, 26f);
                Vector2 pan = (a.deltaPosition + b.deltaPosition) * .5f;
                focus += (-transform.right * pan.x - transform.up * pan.y) * (orbitDistance * .0011f);
                previousPinch = pinch;
            }
        }
        else previousPinch = 0f;
        if (Input.touchCount == 0)
        {
            if (Input.GetMouseButtonDown(0)) previousPointer = Input.mousePosition;
            if (Input.GetMouseButton(0) && !OverTopButtons(Input.mousePosition))
            {
                Vector2 p = Input.mousePosition;
                Vector2 d = p - previousPointer;
                yaw += d.x * .14f;
                pitch = Mathf.Clamp(pitch - d.y * .14f, -12f, 80f);
                previousPointer = p;
            }
            orbitDistance = Mathf.Clamp(orbitDistance - Input.mouseScrollDelta.y * 1.2f, locationIndex==3?2.4f:5f, 26f);
        }
    }
    void UpdateWalk()
    {
        leftStick = Vector2.zero;
        bool hasRightTouch = false;
        for (int i = 0; i < Input.touchCount; i++)
        {
            Touch t = Input.GetTouch(i);
            if (t.phase == TouchPhase.Ended || t.phase == TouchPhase.Canceled)
            {
                if (t.fingerId == leftFinger) leftFinger = -1;
                if (t.fingerId == rightFinger) rightFinger = -1;
                continue;
            }
            // The bottom left half is an independent movement thumbstick.
            if (t.phase == TouchPhase.Began && t.position.x < Screen.width * .43f
                && t.position.y < Screen.height * .54f && leftFinger < 0)
            {
                leftFinger = t.fingerId;
                stickOrigin = t.position;
            }
            else if (t.phase == TouchPhase.Began && t.position.x >= Screen.width * .43f
                && !OverTopButtons(t.position) && rightFinger < 0)
            {
                rightFinger = t.fingerId;
            }
            if (t.fingerId == leftFinger)
                leftStick = Vector2.ClampMagnitude((t.position - stickOrigin) / (Screen.height * .14f), 1f);
            if (t.fingerId == rightFinger && t.phase == TouchPhase.Moved)
            {
                walkYaw += t.deltaPosition.x * .16f;
                lookPitch = Mathf.Clamp(lookPitch - t.deltaPosition.y * .13f, -65f, 65f);
                hasRightTouch = true;
            }
        }
        if (Input.touchCount == 0)
        {
            leftFinger = rightFinger = -1;
            leftStick = new Vector2(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical"));
            if (Input.GetMouseButton(1))
            {
                walkYaw += Input.GetAxis("Mouse X") * 2.8f;
                lookPitch = Mathf.Clamp(lookPitch - Input.GetAxis("Mouse Y") * 2.0f, -65f, 65f);
            }
        }
        Vector3 motion = new Vector3(leftStick.x, 0f, leftStick.y);
        if (motion.sqrMagnitude > 1f) motion.Normalize();
        walker += Quaternion.Euler(0, walkYaw, 0) * motion * (5.1f * Time.deltaTime);
        walker.x = Mathf.Clamp(walker.x, -15.7f, 15.7f);
        walker.z = Mathf.Clamp(walker.z, -16.5f, 16.5f);
        // Surface proxies in the Unity scene allow actual ascent on 18 steps and
        // walking across the observation deck without expensive MeshColliders.
        Vector3 groundTest = new Vector3(walker.x, walker.y + .48f, walker.z);
        if (Physics.Raycast(groundTest, Vector3.down, out RaycastHit surface, 3.15f,
            Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore))
        {
            float desiredEyeHeight = surface.point.y + 1.70f;
            // Ignore a balcony directly overhead or an implausibly tall step.
            if (desiredEyeHeight <= walker.y + .48f)
                walker.y = Mathf.MoveTowards(walker.y, desiredEyeHeight,
                    3.4f * Time.deltaTime);
        }
    }
    bool OverTopButtons(Vector2 point)
    {
        float uiTop = Screen.height - Mathf.Max(110f, Screen.height * .17f);
        return point.y > uiTop;
    }
    void UpdateCamera()
    {
        if (walkMode)
        {
            transform.SetPositionAndRotation(walker, Quaternion.Euler(lookPitch, walkYaw, 0));
        }
        else
        {
            Quaternion q = Quaternion.Euler(pitch, yaw, 0);
            Vector3 proposed = focus - q * Vector3.forward * orbitDistance;
            // The original high-angle orbit started inside the 7m ceiling,
            // making bright overhead rails fill most of the screen.
            proposed.y = Mathf.Clamp(proposed.y, 1.10f, 6.48f);
            transform.position = proposed;
            transform.LookAt(focus, Vector3.up);
        }
    }
    void SelectLocation(int index)
    {
        if (destinations == null || index < 0 || index >= destinations.Length) return;
        locationIndex = index;
        focus = destinations[index].position;
        walkMode = false;
        orbitDistance = index == 0 ? 12.9f : index == 1 ? 12.5f
                      : index == 2 ? 11.6f : 5.8f;
        pitch = index == 2 ? 8f : index==3?15f:11f;
        yaw = index==3?-136f:index==1?-155f:-138f;
    }
    void SwitchMode()
    {
        walkMode = !walkMode;
        leftFinger = rightFinger = -1;
        if (walkMode)
        {
            walker = new Vector3(0f, 1.75f, -10.5f);
            walkYaw = 0f;
            lookPitch = 8f;
        }
        else SelectLocation(locationIndex);
    }
    void EnsureStyles()
    {
        if (headStyle != null) return;
        headStyle = new GUIStyle(GUI.skin.label) {
            fontSize = 22, fontStyle = FontStyle.Bold,
            normal = { textColor = new Color(.91f,.96f,1f) } };
        bodyStyle = new GUIStyle(GUI.skin.label) {
            fontSize = 14, wordWrap = true,
            normal = { textColor = new Color(.72f,.85f,.93f) } };
        tinyStyle = new GUIStyle(GUI.skin.label) {
            fontSize = 13, alignment = TextAnchor.MiddleCenter,
            normal = { textColor = new Color(.85f,.98f,1f) } };
        darkButtonTexture = new Texture2D(2,2,TextureFormat.RGBA32,false);
        darkButtonTexture.SetPixels(new Color[] {
            new Color(.044f,.085f,.12f,.94f),new Color(.044f,.085f,.12f,.94f),
            new Color(.044f,.085f,.12f,.94f),new Color(.044f,.085f,.12f,.94f)
        });
        darkButtonTexture.Apply();
        buttonStyle = new GUIStyle(GUI.skin.button) {
            fontSize = 14, fontStyle = FontStyle.Bold,
            alignment = TextAnchor.MiddleCenter,
            fixedHeight = 0f };
        buttonStyle.normal.background = darkButtonTexture;
        buttonStyle.hover.background = darkButtonTexture;
        buttonStyle.active.background = darkButtonTexture;
        buttonStyle.normal.textColor = new Color(.84f,.94f,1f);
        buttonStyle.hover.textColor = Color.white;
        buttonStyle.active.textColor = new Color(.12f,.88f,1f);
    }
    void OnGUI()
    {
        EnsureStyles();
        float s = Mathf.Clamp(Screen.height / 720f, .7f, 1.6f);
        Matrix4x4 previous = GUI.matrix;
        Color previousColor = GUI.color;
        GUI.matrix = Matrix4x4.Scale(new Vector3(s,s,1));
        float w = Screen.width / s, h = Screen.height / s;

        GUI.color = new Color(.014f,.031f,.052f,.91f);
        GUI.Box(new Rect(12,12,380,79),GUIContent.none);
        GUI.color = new Color(.11f,.84f,.94f);
        GUI.DrawTexture(new Rect(12,12,4,79),Texture2D.whiteTexture);
        GUI.color = Color.white;
        GUI.Label(new Rect(26,21,357,30),"NEON FOUNDRY   /   GARAGE",headStyle);
        GUI.Label(new Rect(26,59,340,24),
            "UNITY 6   •   " + labels[locationIndex] + "   •   " + fps.ToString("0") + " FPS",bodyStyle);

        float x = w - 12;
        if (GUI.Button(new Rect(x-124,17,116,47),walkMode ? "ORBIT VIEW" : "WALK MODE",buttonStyle))
            SwitchMode();
        if (GUI.Button(new Rect(x-244,17,112,47),"OVERLOOK",buttonStyle))
            SelectLocation(2);
        if (GUI.Button(new Rect(x-365,17,113,47),"CELL WORKS",buttonStyle))
            SelectLocation(1);
        if (GUI.Button(new Rect(x-469,17,96,47),"CRAFT",buttonStyle))
            SelectLocation(0);
        if (GUI.Button(new Rect(x-579,17,104,47),"NF-BW01",buttonStyle))
            SelectLocation(3);
        if (locationIndex == 3 && !walkMode)
        {
            GUI.color=new Color(.014f,.031f,.052f,.91f);
            GUI.Box(new Rect(w-227,72,215,45),GUIContent.none);
            GUI.color=Color.white;
            if (GUI.Button(new Rect(w-219,77,199,34),
                guardsVisible ? "HIDE GLASS" : "SHOW GLASS",buttonStyle))
                ToggleGuarding();
        }

        GUI.color = new Color(.014f,.031f,.052f,.76f);
        GUI.Box(new Rect(w*.5f-271,h-51,542,37),GUIContent.none);
        GUI.color = Color.white;
        GUI.Label(new Rect(w*.5f-255,h-43,510,30),
            walkMode ? "LEFT THUMB  Move        RIGHT THUMB  Look        ORBIT VIEW  Exit"
                     : "DRAG  Orbit        PINCH  Zoom        TWO FINGERS  Pan",bodyStyle);

        if (walkMode)
        {
            GUI.color = new Color(.01f,.11f,.19f,.62f);
            GUI.Box(new Rect(34,h-255,166,166), GUIContent.none);
            GUI.color = Color.white;
            GUI.Label(new Rect(48,h-253,138,28),"MOVE",tinyStyle);
            float px = 89 + leftStick.x*49f, py = h-188 - leftStick.y*49f;
            GUI.color = new Color(.10f,.65f,.94f,.7f);
            GUI.Box(new Rect(px-21,py-21,43,43), GUIContent.none);
            GUI.color = Color.white;
        }
        GUI.color = previousColor;
        GUI.matrix = previous;
    }
}

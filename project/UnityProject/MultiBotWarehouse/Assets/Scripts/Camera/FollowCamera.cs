using UnityEngine;

public class FollowCamera : MonoBehaviour
{
    [Header("Setup")]
    [SerializeField]
    private MonoBehaviour nextCam;
    [SerializeField]
    private RobotController controllerScript;
    [SerializeField]
    private GameObject canvas;

    [Header("Follow Settings")]
    [SerializeField]
    private Transform target;
    [SerializeField]
    private float distance = 10f;
    [SerializeField]
    private float zoomSpeed = 5f;
    [SerializeField]
    private float minDistance = 2f;
    [SerializeField]
    private float maxDistance = 20f;

    [Header("Rotation Settings")]
    [SerializeField]
    private float sensitivity = 2f;

    private CameraInputAction cameraInputAction;

    private float yaw = 0f;
    private float pitch = 0f;

    private void Awake()
    {
        cameraInputAction = new CameraInputAction();

        if (target == null)
        {
            Debug.LogError("FollowCamera: No target assigned.");
        }

        cameraInputAction.camera.Switch.performed += _ =>
        {
            nextCam.enabled = true;
            this.enabled = false;
        };

        cameraInputAction.camera.Show.performed += _ =>
        {
            canvas.SetActive(!canvas.activeSelf);
        };
    }

    private void OnEnable()
    {
        cameraInputAction.Enable();
        controllerScript.enabled = true;
    }

    private void OnDisable()
    {
        cameraInputAction.Disable();

        if (controllerScript != null)
            controllerScript.enabled = false;
    }

    private void Update()
    {
        float zoomInput = cameraInputAction.camera.Zoom.ReadValue<float>();
        distance = Mathf.Clamp(distance - zoomInput * zoomSpeed * Time.deltaTime, minDistance, maxDistance);

        if (cameraInputAction.camera.RightClick.ReadValue<float>() > 0.5f)
        {
            Vector2 lookInput = cameraInputAction.camera.Look.ReadValue<Vector2>();
            yaw += lookInput.x * sensitivity;
            pitch -= lookInput.y * sensitivity;
            pitch = Mathf.Clamp(pitch, -90f, 90f);
        }

        Vector3 offset = Quaternion.Euler(pitch, yaw, 0f) * new Vector3(0f, 0f, -distance);

        transform.position = target.position + offset;
        transform.LookAt(target);
    }
}

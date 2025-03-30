using UnityEngine;

public class FollowCamera : MonoBehaviour
{
    [Header("Follow Settings")]
    public Transform target;
    public float distance = 10f;
    public float zoomSpeed = 5f;
    public float minDistance = 2f;
    public float maxDistance = 20f;

    [Header("Rotation Settings")]
    public float sensitivity = 2f;

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
    }

    private void OnEnable()
    {
        cameraInputAction.Enable();
    }

    private void OnDisable()
    {
        cameraInputAction.Disable();
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

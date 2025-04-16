using UnityEngine;

public class FreeCam : MonoBehaviour
{
    [Header("Setup")]
    [SerializeField]
    private MonoBehaviour nextCam;
    [SerializeField]
    private GameObject canvas;

    [Header("Movement Settings")]
    [SerializeField]
    private float moveSpeed = 10f;
    [SerializeField]
    private float boostMultiplier = 2f;
    [SerializeField]
    private float sensitivity = 2f;

    private CameraInputAction cameraInputAction;

    private float yaw = 0f;
    private float pitch = 0f;

    private void Awake()
    {
        cameraInputAction = new CameraInputAction();

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
    }

    private void OnDisable()
    {
        cameraInputAction.Disable();
    }

    private void Update()
    {
        Vector3 moveInput = cameraInputAction.camera.Move.ReadValue<Vector3>();
        Vector2 lookInput = cameraInputAction.camera.Look.ReadValue<Vector2>();
        bool isBoosting = cameraInputAction.camera.Boost.ReadValue<float>() > 0.5f;

        float currentSpeed = isBoosting ? moveSpeed * boostMultiplier : moveSpeed;

        Vector3 moveDirection = transform.right * moveInput.x + transform.forward * moveInput.z + transform.up * moveInput.y;
        transform.position += moveDirection * currentSpeed * Time.deltaTime;

        if (cameraInputAction.camera.RightClick.ReadValue<float>() > 0.5f)
        {
            yaw += lookInput.x * sensitivity;
            pitch -= lookInput.y * sensitivity;
            pitch = Mathf.Clamp(pitch, -90f, 90f);

            transform.eulerAngles = new Vector3(pitch, yaw, 0f);
        }
    }
}


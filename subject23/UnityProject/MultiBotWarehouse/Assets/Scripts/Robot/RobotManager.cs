using System.Threading.Tasks;
using UnityEngine;
using static PlanningSolver.Task;

public class RobotManager : MonoBehaviour
{
    [Header("Setup")]
    [SerializeField]
    private Colors colors;

    [Header("Settings")]
    public Transform storeTransform;
    [SerializeField]
    private float emptyMass = 3f;
    [SerializeField]
    private float loadedMass = 10f;
    [SerializeField]
    private bool colorRandomly = true;

    [Header("Wheel Colliders")]
    [SerializeField]
    private WheelCollider leftWheelCollider;
    [SerializeField]
    private WheelCollider rightWheelCollider;

    [Header("Wheel Transforms")]
    [SerializeField]
    private Transform leftWheelMesh;
    [SerializeField]
    private Transform rightWheelMesh;

    [Header("Movement Settings")]
    [SerializeField]
    private float motorForce = 150f;
    [SerializeField]
    private float turnForce = 30f;

    [Header("Debug")]
    [SerializeField]
    private bool drawDirection = false;
    [SerializeField]
    private bool removeItem = false;

    [HideInInspector]
    public Vector2 control;

    [Header("Monitors")]
    public Item currentItem;

    private Rigidbody robotRigidbody;

    public bool isTaking = true;
    public TaskType taskType = TaskType.Pause;

    private void Awake()
    {
        robotRigidbody = GetComponent<Rigidbody>();

        robotRigidbody.automaticCenterOfMass = false;
        robotRigidbody.centerOfMass = Vector3.zero;

        if (colorRandomly)
            this.gameObject.GetComponentInChildren<MeshRenderer>().sharedMaterial = colors.colors[Random.Range(0, colors.colors.Count)];
    }

    private void FixedUpdate()
    {
        float moveAction = control.x * motorForce;
        float turnAction = control.y * turnForce;

        float leftMotorTorque = moveAction + turnAction;
        float rightMotorTorque = moveAction - turnAction;

        leftWheelCollider.motorTorque = leftMotorTorque;
        rightWheelCollider.motorTorque = rightMotorTorque;

        UpdateWheelPose(leftWheelCollider, leftWheelMesh);
        UpdateWheelPose(rightWheelCollider, rightWheelMesh);

        if (currentItem == null)
            robotRigidbody.mass = emptyMass;
        else
            robotRigidbody.mass = loadedMass;
    }

    private void Update()
    {
        if (drawDirection)
        {
            Debug.DrawRay(transform.position, transform.TransformDirection(Vector3.forward * control.x + Vector3.right * control.y) * 10, Color.green);
        }

        if (removeItem)
        {
            RemoveItem();
            removeItem = false;
        }
    }

    private void UpdateWheelPose(WheelCollider collider, Transform wheelTransform)
    {
        Vector3 pos;
        Quaternion quat;
        collider.GetWorldPose(out pos, out quat);
        wheelTransform.position = pos;
        wheelTransform.rotation = quat * Quaternion.AngleAxis(90, Vector3.up);
    }

    public void RemoveItem()
    {
        Destroy(currentItem.gameObject);
        currentItem = null;
    }
}
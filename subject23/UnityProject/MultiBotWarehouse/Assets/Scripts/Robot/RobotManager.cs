using UnityEngine;

public class RobotManager : MonoBehaviour
{
    [Header("Settings")]
    public Transform storeTransform;

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

    [HideInInspector]
    public Vector2 control;

    [Header("Monitors")]
    public Item currentItem;
    [SerializeField]
    public Vector3Int gridPosition { get { return Wharehouse.convertGridPosition(transform.position); } }

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
    }

    private void Update()
    {
        if (drawDirection)
        {
            Debug.DrawRay(transform.position, transform.TransformDirection(Vector3.forward * control.x + Vector3.right * control.y) * 10, Color.green);
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
}
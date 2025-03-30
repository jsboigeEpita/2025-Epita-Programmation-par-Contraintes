using UnityEngine;

public class RobotManager : MonoBehaviour
{
    [Header("Wheel Colliders")]
    public WheelCollider leftWheelCollider;
    public WheelCollider rightWheelCollider;

    [Header("Wheel Transforms")]
    public Transform leftWheelMesh;
    public Transform rightWheelMesh;

    [Header("Movement Settings")]
    public float motorForce = 150f;
    public float turnForce = 30f;

    [Header("Debug")]
    public bool drawDirection = false;

    [HideInInspector]
    public Vector2 control;

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
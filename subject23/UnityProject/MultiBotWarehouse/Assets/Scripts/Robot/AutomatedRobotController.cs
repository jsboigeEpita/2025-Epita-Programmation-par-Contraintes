using UnityEngine;

[RequireComponent(typeof(RobotManager))]
public class AutomatedRobotController : MonoBehaviour
{
    public Transform target;

    private RobotManager robotManager;

    private void Start()
    {
        robotManager = this.GetComponent<RobotManager>();
    }

    private void Update()
    {
        Vector3 direction = robotManager.transform.InverseTransformDirection(target.position - robotManager.transform.position).normalized;
        robotManager.control = Vector2.up * direction.x + Vector2.right * direction.z;
    }
}

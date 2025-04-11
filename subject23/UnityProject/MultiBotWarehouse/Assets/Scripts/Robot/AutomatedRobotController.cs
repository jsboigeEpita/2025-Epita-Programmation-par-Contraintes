using System;
using UnityEngine;

[RequireComponent(typeof(RobotManager))]
public class AutomatedRobotController : MonoBehaviour
{
    public Vector3 target;
    public float distanceThreshold;

    private RobotManager robotManager;

    private void Start()
    {
        robotManager = this.GetComponent<RobotManager>();
    }

    private void Update()
    {
        Vector3 direction = robotManager.transform.InverseTransformDirection(target - robotManager.transform.position).normalized;
        
        if (Vector2.Distance(new Vector2(robotManager.transform.position.x, robotManager.transform.position.z), new Vector2(target.x, target.z)) < distanceThreshold)
            direction = Vector3.zero;

        robotManager.control = Vector2.up * direction.x + Vector2.right * direction.z;
    }
}

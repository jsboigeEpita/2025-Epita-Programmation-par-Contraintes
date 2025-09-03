using UnityEngine;

[RequireComponent(typeof(RobotManager))]
public class RobotController : MonoBehaviour
{
    private RobotManager robotManager;

    private RobotInputAction robotInputAction;

    private void Awake()
    {
        robotInputAction = new RobotInputAction();
    }

    private void OnEnable()
    {
        robotInputAction.Enable();
    }

    private void OnDisable()
    {
        robotInputAction.Disable();
        robotManager.control = Vector2.zero;
    }

    private void Start()
    {
        robotManager = this.GetComponent<RobotManager>();
    }

    private void Update()
    {
        Vector2 move = robotInputAction.robot.Move.ReadValue<Vector2>();
        robotManager.control = new Vector2(move.y, move.x);
    }
}

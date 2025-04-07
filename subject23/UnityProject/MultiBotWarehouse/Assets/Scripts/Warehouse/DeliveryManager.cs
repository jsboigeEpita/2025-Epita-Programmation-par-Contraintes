using UnityEngine;

public class DeliveryManager : MonoBehaviour
{
    [Header("Setup")]
    [SerializeField]
    private Furnitures furnitures;

    public int[] deliveries;

    private void Awake()
    {
        deliveries = new int[furnitures.furnitures.Count];
    }

    private void TakeFromRobot(RobotManager robotManager)
    {
        deliveries[furnitures.furnitures.FindIndex(ele => robotManager.currentItem.gameObject.name.Contains(ele.name))] += 1;
        Destroy(robotManager.currentItem.gameObject);
        robotManager.currentItem = null;
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.tag == "Robot")
        {
            RobotManager robotManager = other.gameObject.GetComponentInParent<RobotManager>();

            if (robotManager.currentItem != null)
            {
                TakeFromRobot(robotManager);
            }
            else
            {
                Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " without any objects.");
            }
        }
    }
}

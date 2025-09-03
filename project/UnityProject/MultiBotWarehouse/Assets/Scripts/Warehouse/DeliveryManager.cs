using System.Collections.Generic;
using UnityEngine;

public class DeliveryManager : MonoBehaviour
{
    [System.Serializable]
    public class IntArrayWrapper
    {
        public int[] values;

        public IntArrayWrapper(int[] values)
        {
            this.values = values;
        }
    }


    [Header("Setup")]
    [SerializeField]
    private Furnitures furnitures;

    public List<IntArrayWrapper> deliveries;

    private void Awake()
    {
        deliveries = new List<IntArrayWrapper>();
    }

    private void TakeFromRobot(RobotManager robotManager)
    {
        if (robotManager.currentItem.itemIndexes == null)
        {
            deliveries.Add(new IntArrayWrapper(new int[] { robotManager.currentItem.itemIndex }));
        }
        else
        {
            deliveries.Add(new IntArrayWrapper(robotManager.currentItem.itemIndexes.ToArray()));
        }

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
                if (robotManager.currentItem.itemIndexes != null)
                    if (!robotManager.isTaking && robotManager.taskType == PlanningSolver.Task.TaskType.Packer)
                        TakeFromRobot(robotManager);
                else
                    Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " with an item (without packing).");
            }
            else
            {
                Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " without any objects.");
            }
        }
    }
}

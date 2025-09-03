using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;

public class PackerInputManager : MonoBehaviour
{
    public PackerManager packerManager;

    private void TakeFromRobot(RobotManager robotManager)
    {
        Item taken = robotManager.currentItem;
        robotManager.currentItem = null;

        taken.transform.SetParent(this.transform);
        taken.gameObject.SetActive(false);
        packerManager.AddToBuffer(taken);
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.tag == "Robot")
        {
            RobotManager robotManager = other.gameObject.GetComponentInParent<RobotManager>();

            if (robotManager.currentItem != null)
            {
                if (robotManager.currentItem.itemIndexes == null)
                    if (!robotManager.isTaking && robotManager.taskType == PlanningSolver.Task.TaskType.Shelf)
                        TakeFromRobot(robotManager);
                else
                    Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " with a box.");
            }
            else
            {
                Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " without any objects.");
            }
        }
    }
}

using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using UnityEngine;

public class PackerOutputManager : MonoBehaviour
{
    [SerializeField]
    private GameObject boxPrefab;
    [SerializeField]
    private float scale;
    [SerializeField]
    private Vector3 offset;

    public PackerManager packerManager;

    private void PutOnRobot(RobotManager robotManager)
    {
        List<Item> buffer = packerManager.GetBuffer();

        robotManager.currentItem = GameObject.Instantiate(boxPrefab).AddComponent<Item>();
        robotManager.currentItem.itemIndexes = buffer.Select(ele => ele.itemIndex).ToList();
        robotManager.currentItem.transform.SetParent(robotManager.storeTransform);
        robotManager.currentItem.transform.localPosition = offset;
        robotManager.currentItem.transform.localScale = Vector3.one * scale;

        buffer.Clear();
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.tag == "Robot")
        {
            RobotManager robotManager = other.gameObject.GetComponentInParent<RobotManager>();

            if (robotManager.currentItem == null)
            {
                if (packerManager.GetBuffer().Count != 0)
                    if (robotManager.isTaking && robotManager.taskType == PlanningSolver.Task.TaskType.Packer)
                        PutOnRobot(robotManager);
                else
                    Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " but there was nothing to pickup.");
            }
            else
            {
                Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " with an object.");
            }
        }
    }
}

using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using Unity.VisualScripting;
using UnityEngine;
using static UnityEngine.Rendering.DebugUI;

public class Shelf : MonoBehaviour
{
    public Item currentItem;

    private Vector3 storePosition;
    private string itemName;

    public void Initialize(Vector3 storePosition, string itemName)
    {
        this.storePosition = storePosition;
        this.itemName = itemName;
    }

    public void takeFromRobot(RobotManager robotManager)
    {
        if (!robotManager.currentItem.gameObject.name.Contains(itemName))
        {
            Debug.LogError(robotManager.name + " arrived to " + this.name + " with an object of the wrong type.");
            return;
        }

        currentItem = robotManager.currentItem;
        robotManager.currentItem = null;

        currentItem.transform.SetParent(this.transform);
        currentItem.transform.localPosition = storePosition + Vector3.up * currentItem.itemCollider.bounds.size.y / 2;
    }

    public void putOnRobot(RobotManager robotManager)
    {
        robotManager.currentItem = currentItem;
        currentItem = null;

        robotManager.currentItem.transform.SetParent(robotManager.storeTransform);
        robotManager.currentItem.transform.localPosition = Vector3.up * robotManager.currentItem.itemCollider.bounds.size.y / 2;
    }
}

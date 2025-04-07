using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using Unity.VisualScripting;
using UnityEngine;
using static UnityEngine.Rendering.DebugUI;

public class Loader : MonoBehaviour
{
    private BoxCollider boxCollider;
    private BoxCollider boxTrigger;

    private Func<string, bool> captureColliderFunc;

    private List<(Collider, Transform)> capturedColliders;

    public void Initialize(BoxCollider boxCollider, BoxCollider boxTrigger, Func<string, bool> captureColliderFunc)
    {
        this.boxCollider = boxCollider;
        this.boxTrigger = boxTrigger;
        this.captureColliderFunc = captureColliderFunc;

        this.capturedColliders = new List<(Collider, Transform)>();
    }

    private void OnTriggerEnter(Collider other)
    {
        if (this.boxTrigger.enabled)
        {
            if (captureColliderFunc(other.gameObject.name))
            {
                capturedColliders.Add((other, other.transform.parent));
                other.transform.SetParent(this.transform);
            }
        }
    }

    private void OnTriggerExit(Collider other)
    {
        if (this.boxTrigger.enabled)
        {
            (int index, (Collider, Transform))[] search = capturedColliders.Select((captured, index) => (index, captured)).Where(capturedWithIndex => capturedWithIndex.Item2.Item1 == other).ToArray();
            
            if (search.Length == 1)
            {
                (int index, (Collider, Transform)) capturedColliderWithIndex = search[0];
                capturedColliderWithIndex.Item2.Item1.transform.SetParent(capturedColliderWithIndex.Item2.Item2);
                capturedColliders.RemoveAt(capturedColliderWithIndex.index);
            }
            else if (search.Length > 1)
            {
                Debug.LogError(this.name + " has a collider that has been found " + search.Length + " times: " + search.ToString());
            }
        }
    }

    public void Activate()
    {
        this.boxTrigger.enabled = true;
    }

    public void Deactivate()
    {
        this.boxTrigger.enabled = false;
        ReleaseAll();
    }

    public void ReleaseAll()
    {
        foreach (var capturedCollider in capturedColliders)
        {
            capturedCollider.Item1.transform.SetParent(capturedCollider.Item2);
        }

        capturedColliders.Clear();
    }
}

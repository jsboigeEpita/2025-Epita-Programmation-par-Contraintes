using System.Collections.Generic;
using UnityEngine;

public class RayCastSystem : MonoBehaviour
{
    [SerializeField] public int raycastLength;
    [SerializeField] public LayerMask ignored_masks;
    [SerializeField] List<string> hittableTags;

    [SerializeField] List<Transform> raycast_transforms;

    private float[] distances;

    private void Awake()
    {
        this.distances = new float[raycast_transforms.Count];
        for (int i = 0; i < raycast_transforms.Count; i++)
        {
            this.distances[i] = this.raycastLength;
        }
    }

    public float[] getDistances()
    {
        return this.distances;
    }

    private void FixedUpdate()
    {
        this.CreateRaycasts();
    }

    public void CreateRaycasts()
    {
        RaycastHit hit;
        int i = 0;
        foreach (Transform t in this.raycast_transforms)
        {
            if (Physics.Raycast(t.position, t.forward, out hit, this.raycastLength, ~this.ignored_masks) && this.hittableTags.Contains(hit.transform.gameObject.tag))
            {
                this.distances[i++] = hit.distance;
                Debug.DrawRay(t.position, t.forward * hit.distance, Color.red);
            }
            else
            {
                Debug.DrawRay(t.position, t.forward * this.raycastLength, Color.white);
                this.distances[i++] = this.raycastLength;
            }
        }
    }
}

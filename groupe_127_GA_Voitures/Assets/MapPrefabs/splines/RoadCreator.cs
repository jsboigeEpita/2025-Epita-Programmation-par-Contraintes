using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Splines;

public class SplineRoadCreator : MonoBehaviour
{
    public Spline spline;
    public GameObject roadPrefab;
    public List<Vector3> checkpoints = new List<Vector3>();
    private List<GameObject> menuSpawnedGO;

    void Awake()
    {
        this.menuSpawnedGO = new List<GameObject>();
        GameObject spline_go = GameObject.FindGameObjectWithTag("Spline");
        if (spline_go != null) {
            this.spline = spline_go.GetComponent<SplineContainer>().Spline;
            CreateRoadAlongSpline();
        }
    }

    public void CreateMenuSpline(Spline spline)
    {
        float length = SplineUtility.CalculateLength(spline, transform.localToWorldMatrix);
        float spacing = 0.1f;
        int numSegments = Mathf.CeilToInt(length / spacing);
        for (int i = 0; i < numSegments; i++)
        {
            float t = i / (float)(numSegments - 1);
            Vector3 position = spline.EvaluatePosition(t);
            Vector3 tangent = spline.EvaluateTangent(t);
            Quaternion rotation = Quaternion.LookRotation(tangent);
            GameObject roadSegment = Instantiate(roadPrefab, position, rotation);
            this.menuSpawnedGO.Add(roadSegment);
        }
    }
    public void DestroyMenuSpline()
    {
        foreach (GameObject go in this.menuSpawnedGO)
        {
            Destroy(go);
        }
        this.menuSpawnedGO.Clear();
    }

    void CreateRoadAlongSpline()
    {
        float length = SplineUtility.CalculateLength(spline, transform.localToWorldMatrix);
        float spacing = 0.1f;
        int numSegments = Mathf.CeilToInt(length / spacing);
        for (int i = 0; i < numSegments; i++)
        {
            float t = i / (float)(numSegments - 1);
            Vector3 position = spline.EvaluatePosition(t);
            Vector3 tangent = spline.EvaluateTangent(t);
            Quaternion rotation = Quaternion.LookRotation(tangent);
            GameObject roadSegment = Instantiate(roadPrefab, position, rotation);

            // Activate start line
            if (i == 0)
            {
                foreach (MeshRenderer mr in roadSegment.GetComponentsInChildren<MeshRenderer>())
                {
                    if (mr.gameObject.name.Equals("Start")) {
                        mr.enabled = true;
                    }
                }
            }

            // Activate finish line
            if (i == numSegments - 100)
            {
                foreach (MeshRenderer mr in roadSegment.GetComponentsInChildren<MeshRenderer>())
                {
                    if (mr.gameObject.name.Equals("Finish")) {
                        mr.enabled = true;
                    }
                }
            }

            // Remove last checkpoints so it loops nicely
            if (i % 25 != 24 || i >= numSegments - 100)
            {
                DestroyImmediate(roadSegment.transform.Find("Checkpoint").gameObject);
                continue;
            }
            this.checkpoints.Add(roadSegment.transform.Find("Checkpoint").transform.position);
        }
    }
}

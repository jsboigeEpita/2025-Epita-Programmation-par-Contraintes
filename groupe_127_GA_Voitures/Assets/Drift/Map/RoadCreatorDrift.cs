using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Splines;

public class SplineRoadCreatorDrift : MonoBehaviour
{
    public SplineContainer splineContainer;
    public Spline spline;
    public GameObject roadPrefab;
    public List<Vector3> checkpoints = new List<Vector3>();

    void Awake()
    {
        this.spline = this.splineContainer.Spline;
        CreateRoadAlongSpline();
    }

    void CreateRoadAlongSpline()
    {
        float length = SplineUtility.CalculateLength(spline, transform.localToWorldMatrix);
        float spacing = 0.5f;
        int numSegments = Mathf.CeilToInt(length / spacing);
        for (int i = 0; i < numSegments; i++)
        {
            float t = i / (float)(numSegments - 1);
            Vector3 position = spline.EvaluatePosition(t);
            Vector3 tangent = spline.EvaluateTangent(t);
            Quaternion rotation = Quaternion.LookRotation(tangent);
            GameObject roadSegment = Instantiate(roadPrefab, position, rotation);
            if (i % 5 != 4 || i > numSegments - 20) {
                DestroyImmediate(roadSegment.transform.Find("Checkpoint").gameObject);
                continue;
            }
            this.checkpoints.Add(roadSegment.transform.Find("Checkpoint").transform.position);
        }
    }
}

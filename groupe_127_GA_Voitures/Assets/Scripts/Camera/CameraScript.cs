using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;

public class CameraScript : MonoBehaviour
{
    public GameObject toFollow;

    private void FixedUpdate()
    {
        if (this.toFollow != null && this.toFollow.GetComponent<CarController>().canMove)
        {
            this.transform.position = this.toFollow.transform.position + new Vector3(0, 50, 0);
            this.transform.LookAt(this.toFollow.transform);
        }
    }

    public void resetToFollow()
    {
        this.toFollow = null;
    }
}

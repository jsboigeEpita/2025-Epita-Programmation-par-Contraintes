using System;
using UnityEngine;

[Serializable]
public class Neuron
{
    [SerializeField] public int n_inputs;
    [SerializeField] public float[] weights;
    [SerializeField] public float bias;
    public Neuron(int n_inputs)
    {
        this.n_inputs = n_inputs;
        this.weights = new float[this.n_inputs];
        for (int i = 0; i < this.n_inputs; i++)
        {
            this.weights[i] = 0;
        }
        this.bias = 0;
    }

    public float Forward(float[] inputs)
    {
        float result = this.bias;
        for (int i = 0; i < this.n_inputs; i++)
        {
            result += this.weights[i] * inputs[i];
        }
        return result;
    }

    // MUTATION
    public void Mutate(float proba, float amount)
    {
        for (int i = 0; i < this.n_inputs; i++)
        {
            if (UnityEngine.Random.value <= proba)
            {
                this.weights[i] += UnityEngine.Random.Range(-1.0f, 1.0f) * amount;
            }
        }
        if (UnityEngine.Random.value <= proba)
        {
            this.bias += UnityEngine.Random.Range(-1.0f, 1.0f) * amount;
        }
    }

    // DEEP COPY
    public Neuron DeepCopy()
    {
        Neuron result = new Neuron(this.n_inputs);
        result.bias = this.bias;
        result.weights = (float[])this.weights.Clone();
        return result;
    }
}

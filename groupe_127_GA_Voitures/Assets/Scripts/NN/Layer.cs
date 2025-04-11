using System;
using UnityEngine;

public enum ActivationMethod
{
    ReLU,
    Sigmoid,
    Tanh,
}

[Serializable]
public class Layer
{
    [SerializeField] public int n_inputs;
    [SerializeField] public int n_outputs;
    [SerializeField] public float[] outputs;
    [SerializeField] public Neuron[] neurons;
    [SerializeField] public ActivationMethod activationMethod;

    public Layer(int n_inputs, int n_outputs, ActivationMethod activation_method)
    {
        this.n_inputs = n_inputs;
        this.n_outputs = n_outputs;
        this.neurons = new Neuron[this.n_outputs];
        for (int i = 0; i < this.n_outputs; i++)
        {
            this.neurons[i] = new Neuron(this.n_inputs);
        }
        this.activationMethod = activation_method;
        this.outputs = new float[this.n_outputs];
    }

    public void Forward(float[] inputs)
    {
        for (int i = 0; i < this.n_outputs; i++)
        {
            float result = this.neurons[i].Forward(inputs);
            if (this.activationMethod == ActivationMethod.ReLU)
            {
                this.outputs[i] = this.ReLUActivation(result);
            }
            else if (this.activationMethod == ActivationMethod.Sigmoid)
            {
                this.outputs[i] = this.SigmoidActivation(result);
            }
            else if (this.activationMethod == ActivationMethod.Tanh)
            {
                this.outputs[i] = this.TanhActivation(result);
            }
        }
    }

    // ACTIVATION FUNCTIONS
    public float ReLUActivation(float input)
    {
        return Math.Max(0, input);
    }

    public float SigmoidActivation(float input)
    {
        float result = 1f / (1 + Mathf.Exp(-input));
        result -= 0.5f;
        result *= 2f;
        return result;
    }

    public float TanhActivation(float input)
    {
        float result = Mathf.Exp(input) - Mathf.Exp(-input);
        result = result / (Mathf.Exp(input) + Mathf.Exp(-input));
        return result;
    }

    // MUTATION
    public void Mutate(float proba, float amount)
    {
        for (int i = 0; i < this.n_outputs; i++)
        {
            this.neurons[i].Mutate(proba, amount);
        }
    }

    // DEEP COPY
    public Layer DeepCopy()
    {
        Layer result = new Layer(this.n_inputs, this.n_outputs, this.activationMethod);
        for (int i = 0; i < this.n_outputs; i++)
        {
            result.neurons[i] = this.neurons[i].DeepCopy();
        }
        result.outputs = (float[])this.outputs.Clone();
        return result;
    }
}

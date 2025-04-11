#pragma once

#include "../include/singleton.hh"

template <typename T>
T& Singleton<T>::instance()
{
    static T inst;
    return inst;
}

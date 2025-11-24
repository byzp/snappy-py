#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "snappy-c.h"

#ifndef Py_MOD_GIL_NOT_USED
#  define Py_MOD_GIL_NOT_USED 0
#endif

PyDoc_STRVAR(compress_doc,
"compress(data, /)\n--\n\nCompress data using Snappy algorithm.");

static PyObject *
py_snappy_compress(PyObject *self, PyObject *arg)
{
    Py_buffer input;
    PyObject *result;
    size_t max_len, actual_len;
    snappy_status status;
    char *output_buffer;

    // 使用METH_O直接获取buffer
    if (PyObject_GetBuffer(arg, &input, PyBUF_SIMPLE) < 0) {
        return NULL;
    }

    max_len = snappy_max_compressed_length((size_t)input.len);
    if (max_len > PY_SSIZE_T_MAX) {
        PyBuffer_Release(&input);
        return PyErr_NoMemory();
    }

    result = PyBytes_FromStringAndSize(NULL, (Py_ssize_t)max_len);
    if (result == NULL) {
        PyBuffer_Release(&input);
        return NULL;
    }

    output_buffer = PyBytes_AS_STRING(result);
    actual_len = max_len;

    Py_BEGIN_ALLOW_THREADS
    status = snappy_compress(
        (const char *)input.buf,
        (size_t)input.len,
        output_buffer,
        &actual_len
    );
    Py_END_ALLOW_THREADS

    PyBuffer_Release(&input);

    if (status != SNAPPY_OK) {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Snappy compression failed");
        return NULL;
    }

    // 如果实际长度小于最大预估长度, 调整 bytes 对象大小
    if (actual_len < max_len) {
        if (_PyBytes_Resize(&result, (Py_ssize_t)actual_len) < 0) {
            return NULL;
        }
    }

    return result;
}

PyDoc_STRVAR(uncompress_doc,
"uncompress(data, /)\n--\n\nDecompress Snappy-compressed data.");

static PyObject *
py_snappy_uncompress(PyObject *self, PyObject *arg)
{
    Py_buffer input;
    PyObject *result;
    size_t output_length;
    snappy_status status;
    char *output_buffer;

    if (PyObject_GetBuffer(arg, &input, PyBUF_SIMPLE) < 0) {
        return NULL;
    }

    // 获取解压后长度
    status = snappy_uncompressed_length(
        (const char *)input.buf,
        (size_t)input.len,
        &output_length
    );

    if (status != SNAPPY_OK) {
        PyBuffer_Release(&input);
        PyErr_SetString(PyExc_RuntimeError, "Invalid Snappy data");
        return NULL;
    }

    if (output_length > PY_SSIZE_T_MAX) {
        PyBuffer_Release(&input);
        return PyErr_NoMemory();
    }

    // 直接分配目标py对象，避免中间 malloc 和 memcpy
    result = PyBytes_FromStringAndSize(NULL, (Py_ssize_t)output_length);
    if (result == NULL) {
        PyBuffer_Release(&input);
        return NULL;
    }

    output_buffer = PyBytes_AS_STRING(result);

    //直接写入py对象内存
    Py_BEGIN_ALLOW_THREADS
    status = snappy_uncompress(
        (const char *)input.buf,
        (size_t)input.len,
        output_buffer,
        &output_length
    );
    Py_END_ALLOW_THREADS

    PyBuffer_Release(&input);

    if (status != SNAPPY_OK) {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Snappy decompression failed");
        return NULL;
    }

    return result;
}

static PyMethodDef snappy_methods[] = {
    {"compress", py_snappy_compress, METH_O, compress_doc},
    {"uncompress", py_snappy_uncompress, METH_O, uncompress_doc},
    {"decompress", py_snappy_uncompress, METH_O, uncompress_doc},
    {NULL, NULL, 0, NULL}
};

static PyModuleDef_Slot snappy_slots[] = {
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, NULL}
};

static struct PyModuleDef snappy_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "snappy_py",
    .m_doc = "Snappy compression module (Free-threaded compatible)",
    .m_size = 0,
    .m_methods = snappy_methods,
    .m_slots = snappy_slots,
};

PyMODINIT_FUNC
PyInit_snappy_py(void)
{
    return PyModuleDef_Init(&snappy_module);
}
/*
 * Support routines from the Windows API
 *
 * This module was originally created by merging PC/_subprocess.c with
 * Modules/_multiprocessing/win32_functions.c.
 *
 * Copyright (c) 2004 by Fredrik Lundh <fredrik@pythonware.com>
 * Copyright (c) 2004 by Secret Labs AB, http://www.pythonware.com
 * Copyright (c) 2004 by Peter Astrand <astrand@lysator.liu.se>
 *
 * By obtaining, using, and/or copying this software and/or its
 * associated documentation, you agree that you have read, understood,
 * and will comply with the following terms and conditions:
 *
 * Permission to use, copy, modify, and distribute this software and
 * its associated documentation for any purpose and without fee is
 * hereby granted, provided that the above copyright notice appears in
 * all copies, and that both that copyright notice and this permission
 * notice appear in supporting documentation, and that the name of the
 * authors not be used in advertising or publicity pertaining to
 * distribution of the software without specific, written prior
 * permission.
 *
 * THE AUTHORS DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
 * INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.
 * IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY SPECIAL, INDIRECT OR
 * CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
 * OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
 * NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
 * WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 */

/* Licensed to PSF under a Contributor Agreement. */
/* See http://www.python.org/2.4/license for licensing details. */

#include <Python.h>
#include "structmember.h"

#define WINDOWS_LEAN_AND_MEAN
#include "windows.h"
#include <crtdbg.h>

#if defined(MS_WIN32) && !defined(MS_WIN64)
#define HANDLE_TO_PYNUM(handle) \
    PyLong_FromUnsignedLong((unsigned long) handle)
#define PYNUM_TO_HANDLE(obj) ((HANDLE)PyLong_AsUnsignedLong(obj))
#define F_POINTER "k"
#define T_POINTER T_ULONG
#else
#define HANDLE_TO_PYNUM(handle) \
    PyLong_FromUnsignedLongLong((unsigned long long) handle)
#define PYNUM_TO_HANDLE(obj) ((HANDLE)PyLong_AsUnsignedLongLong(obj))
#define F_POINTER "K"
#define T_POINTER T_ULONGLONG
#endif

#define F_HANDLE F_POINTER
#define F_DWORD "k"

int
_PyLong_Size_t_Converter(PyObject *obj, void *ptr)
{
    size_t uval;

    if (PyLong_Check(obj) && _PyLong_Sign(obj) < 0) {
        PyErr_SetString(PyExc_ValueError, "value must be positive");
        return 0;
    }
    uval = PyLong_AsSize_t(obj);
    if (uval == (size_t)-1 && PyErr_Occurred())
        return 0;

    *(size_t *)ptr = uval;
    return 1;
}

/*[clinic input]
module _winshmem
[clinic start generated code]*/
/*[clinic end generated code: output=da39a3ee5e6b4b0d input=36caa4ba4cca31ae]*/

/*[python input]
def create_converter(type_, format_unit):
    name = type_ + '_converter'
    # registered upon creation by CConverter's metaclass
    type(name, (CConverter,), {'type': type_, 'format_unit': format_unit})
# format unit differs between platforms for these
create_converter('HANDLE', '" F_HANDLE "')
create_converter('HMODULE', '" F_HANDLE "')
create_converter('LPSECURITY_ATTRIBUTES', '" F_POINTER "')
create_converter('LPCVOID', '" F_POINTER "')
create_converter('BOOL', 'i') # F_BOOL used previously (always 'i')
create_converter('DWORD', 'k') # F_DWORD is always "k" (which is much shorter)
create_converter('LPCTSTR', 's')
create_converter('LPCWSTR', 'u')
create_converter('LPWSTR', 'u')
create_converter('UINT', 'I') # F_UINT used previously (always 'I')
class HANDLE_return_converter(CReturnConverter):
    type = 'HANDLE'
    def render(self, function, data):
        self.declare(data)
        self.err_occurred_if("_return_value == INVALID_HANDLE_VALUE", data)
        data.return_conversion.append(
            'if (_return_value == NULL) {\n    Py_RETURN_NONE;\n}\n')
        data.return_conversion.append(
            'return_value = HANDLE_TO_PYNUM(_return_value);\n')
class DWORD_return_converter(CReturnConverter):
    type = 'DWORD'
    def render(self, function, data):
        self.declare(data)
        self.err_occurred_if("_return_value == PY_DWORD_MAX", data)
        data.return_conversion.append(
            'return_value = Py_BuildValue("k", _return_value);\n')
class LPVOID_return_converter(CReturnConverter):
    type = 'LPVOID'
    def render(self, function, data):
        self.declare(data)
        self.err_occurred_if("_return_value == NULL", data)
        data.return_conversion.append(
            'return_value = HANDLE_TO_PYNUM(_return_value);\n')
[python start generated code]*/
/*[python end generated code: output=da39a3ee5e6b4b0d input=c9540cfb622cf0bc]*/

/*[clinic input]
_winshmem.CreateFileMapping -> HANDLE
    file_handle: HANDLE
    security_attributes: LPSECURITY_ATTRIBUTES
    protect: DWORD
    max_size_high: DWORD
    max_size_low: DWORD
    name: LPCWSTR
    /
[clinic start generated code]*/

static HANDLE
_winshmem_CreateFileMapping_impl(PyObject *module, HANDLE file_handle,
                                 LPSECURITY_ATTRIBUTES security_attributes,
                                 DWORD protect, DWORD max_size_high,
                                 DWORD max_size_low, LPCWSTR name)
/*[clinic end generated code: output=1ea4a6917022df1f input=8edee50ee30e319c]*/
{
    HANDLE handle;

    Py_BEGIN_ALLOW_THREADS
    handle = CreateFileMappingW(file_handle, security_attributes,
                                protect, max_size_high, max_size_low,
                                name);
    Py_END_ALLOW_THREADS

    if (handle == NULL) {
        PyObject *temp = PyUnicode_FromWideChar(name, -1);
        PyErr_SetExcFromWindowsErrWithFilenameObject(PyExc_OSError, 0, temp);
        Py_XDECREF(temp);
        handle = INVALID_HANDLE_VALUE;
    }

    return handle;
}

/*[clinic input]
_winshmem.OpenFileMapping -> HANDLE
    desired_access: DWORD
    inherit_handle: BOOL
    name: LPCWSTR
    /
[clinic start generated code]*/

static HANDLE
_winshmem_OpenFileMapping_impl(PyObject *module, DWORD desired_access,
                               BOOL inherit_handle, LPCWSTR name)
/*[clinic end generated code: output=27d05fde662c60d9 input=c858eb3390069697]*/
{
    HANDLE handle;

    Py_BEGIN_ALLOW_THREADS
    handle = OpenFileMappingW(desired_access, inherit_handle, name);
    Py_END_ALLOW_THREADS

    if (handle == NULL) {
        PyObject *temp = PyUnicode_FromWideChar(name, -1);
        PyErr_SetExcFromWindowsErrWithFilenameObject(PyExc_OSError, 0, temp);
        Py_XDECREF(temp);
        handle = INVALID_HANDLE_VALUE;
    }

    return handle;
}

/*[clinic input]
_winshmem.MapViewOfFile -> LPVOID
    file_map: HANDLE
    desired_access: DWORD
    file_offset_high: DWORD
    file_offset_low: DWORD
    number_bytes: size_t
    /
[clinic start generated code]*/

static LPVOID
_winshmem_MapViewOfFile_impl(PyObject *module, HANDLE file_map,
                             DWORD desired_access, DWORD file_offset_high,
                             DWORD file_offset_low, size_t number_bytes)
/*[clinic end generated code: output=ec6595e478fc7329 input=b849287620ecd259]*/
{
    LPVOID address;

    Py_BEGIN_ALLOW_THREADS
    address = MapViewOfFile(file_map, desired_access, file_offset_high,
                            file_offset_low, number_bytes);
    Py_END_ALLOW_THREADS

    if (address == NULL)
        PyErr_SetFromWindowsErr(0);

    return address;
}

/*[clinic input]
_winshmem.VirtualQuerySize -> size_t
    address: LPCVOID
    /
[clinic start generated code]*/

static size_t
_winshmem_VirtualQuerySize_impl(PyObject *module, LPCVOID address)
/*[clinic end generated code: output=e387720b0fc827c8 input=9cb9ea8cc02f36d9]*/
{
    SIZE_T size_of_buf;
    MEMORY_BASIC_INFORMATION mem_basic_info;
    SIZE_T region_size;

    Py_BEGIN_ALLOW_THREADS
    size_of_buf = VirtualQuery(address, &mem_basic_info, sizeof(mem_basic_info));
    Py_END_ALLOW_THREADS

    if (size_of_buf == 0)
        PyErr_SetFromWindowsErr(0);

    region_size = mem_basic_info.RegionSize;
    return region_size;
}

/*[clinic input]
_winshmem.UnmapViewOfFile
    address: LPCVOID
    /
[clinic start generated code]*/

static PyObject *
_winshmem_UnmapViewOfFile_impl(PyObject *module, LPCVOID address)
/*[clinic end generated code: output=0c5e521bc21e44f6 input=094db9950e24bbbe]*/
{
    BOOL success;

    Py_BEGIN_ALLOW_THREADS
    success = UnmapViewOfFile(address);
    Py_END_ALLOW_THREADS

    if (!success) {
        return PyErr_SetFromWindowsErr(0);
    }

    Py_RETURN_NONE;
}

#include "clinic/winshmem.c.h"

static PyMethodDef module_methods[ ] = {
    _WINSHMEM_CREATEFILEMAPPING_METHODDEF
    _WINSHMEM_MAPVIEWOFFILE_METHODDEF
    _WINSHMEM_OPENFILEMAPPING_METHODDEF
    _WINSHMEM_VIRTUALQUERYSIZE_METHODDEF
    _WINSHMEM_UNMAPVIEWOFFILE_METHODDEF
    {NULL} /* Sentinel */
};

static struct PyModuleDef this_module = {
    PyModuleDef_HEAD_INIT,  // m_base
    "_winshmem",          // m_name
    "Windows shared memory module",     // m_doc
    -1,                     // m_size (space allocated for module globals)
    module_methods,         // m_methods
};

#define WINAPI_CONSTANT(fmt, con) \
    PyDict_SetItemString(d, #con, Py_BuildValue(fmt, con))

/* Module init function */
PyMODINIT_FUNC
PyInit__winshmem(void) {
    PyObject *d;
    PyObject *module;
    module = PyModule_Create(&this_module);
    if (!module) {
        return NULL;
    }
    d = PyModule_GetDict(module);

    // constants
    WINAPI_CONSTANT(F_DWORD, FILE_MAP_ALL_ACCESS);
    WINAPI_CONSTANT(F_DWORD, FILE_MAP_COPY);
    WINAPI_CONSTANT(F_DWORD, FILE_MAP_EXECUTE);
    WINAPI_CONSTANT(F_DWORD, FILE_MAP_READ);
    WINAPI_CONSTANT(F_DWORD, FILE_MAP_WRITE);
    WINAPI_CONSTANT(F_HANDLE, INVALID_HANDLE_VALUE);
    WINAPI_CONSTANT(F_DWORD, PAGE_EXECUTE);
    WINAPI_CONSTANT(F_DWORD, PAGE_EXECUTE_READ);
    WINAPI_CONSTANT(F_DWORD, PAGE_EXECUTE_READWRITE);
    WINAPI_CONSTANT(F_DWORD, PAGE_EXECUTE_WRITECOPY);
    WINAPI_CONSTANT(F_DWORD, PAGE_GUARD);
    WINAPI_CONSTANT(F_DWORD, PAGE_NOACCESS);
    WINAPI_CONSTANT(F_DWORD, PAGE_NOCACHE);
    WINAPI_CONSTANT(F_DWORD, PAGE_READONLY);
    WINAPI_CONSTANT(F_DWORD, PAGE_READWRITE);
    WINAPI_CONSTANT(F_DWORD, PAGE_WRITECOMBINE);
    WINAPI_CONSTANT(F_DWORD, PAGE_WRITECOPY);
    return module;
}

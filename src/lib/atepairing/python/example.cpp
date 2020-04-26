#include "example.h"

#include "bn.h"
#include "zm.h"
#include "test_point.hpp"
#include <iostream>

using namespace mie;
using namespace bn;

typedef ZmZ<Vuint, Vuint> GF;

// Global Generators
Ec1* g1 = NULL;
Ec2* g2 = NULL;

// Setup

void setup()
{
  // Create generators
  CurveParam cp = CurveFp254BNb;
  Param::init(cp);
  
  const Point& pt = selectPoint(cp);
  g1 = new Ec1(pt.g1.a, pt.g1.b);
  g2 = new Ec2(
	   Fp2(Fp(pt.g2.aa), Fp(pt.g2.ab)),
	   Fp2(Fp(pt.g2.ba), Fp(pt.g2.bb))
	   );
}

GF* new_gf(unsigned long long n) {
  GF* a = new GF(n); 
  a->setModulo(Param::r);
  return a;
}

void delete_gf(GF* a) {
  delete a;
}

void add(GF* a, GF* b, GF* c) {
  *a = *b + *c;
}

void sub(GF* a, GF* b, GF* c) {
  *a = *b - *c;
}

void mul(GF* a, GF* b, GF* c) {
  *a = *b * *c;
}

void div(GF* a, GF* b, GF* c) {
  *a = *b / *c;
}

void neg(GF* a, GF* b) {
  *a = -(*b);
}

void inv(GF* a, GF* b) {
  // Do we need a call to a.setModulo(Param::r); ?
  GF::inv(*b, *a);    // Copied from _fuop.  Is this really the right order of args?
}

std::string to_string(GF* a) {
  return a->toString();
}

/*
// Ec1 Operations

static PyObject *
get_g1(PyObject *args, PyObject *self)
{
  return Ec1_tup(g1);
}

static PyObject *
ec1smul(PyObject *self, PyObject *args)
{

  PyObject * t;
  const char * aStr;

  PyArg_ParseTuple(args, "Os", &t, &aStr);

  Ec1 e = tup_Ec1(t);

  
  GF a = str_GF(aStr);

  return Ec1_tup(e * a);

}

static PyObject *
ec1add(PyObject *self, PyObject *args)
{

  
  PyObject * t1;
  PyObject * t2;

  PyArg_ParseTuple(args, "OO", &t1, &t2);

  Ec1 e1 = tup_Ec1(t1);
  Ec1 e2 = tup_Ec1(t2);

  return Ec1_tup(e2 + e1);
  
}

static PyObject *
ec1sub(PyObject *self, PyObject *args)
{

  PyObject * t1;
  PyObject * t2;

  PyArg_ParseTuple(args, "OO", &t1, &t2);

  Ec1 e1 = tup_Ec1(t1);
  Ec1 e2 = tup_Ec1(t2);

  return Ec1_tup(e1 - e2);


}

static PyObject *
ec1eq(PyObject *self, PyObject * args)
{
  PyObject * t1;
  PyObject * t2;

  PyArg_ParseTuple(args, "OO", &t1, &t2);

  Ec1 e1 = tup_Ec1(t1);
  Ec1 e2 = tup_Ec1(t2);

  if (e1 == e2){
    return Py_True;
  } else {
    return Py_False;
  }
  
}


// Ec2 Operations

static PyObject *
get_g2(PyObject *args, PyObject *self)
{
  return Ec2_tup(g2);
}

static PyObject *
ec2smul(PyObject *self, PyObject *args)
{

  PyObject * t;
  const char * aStr;

  PyArg_ParseTuple(args, "Os", &t, &aStr);

  Ec2 e = tup_Ec2(t);
  GF a = str_GF(aStr);

  return Ec2_tup(e * a);

}

static PyObject *
ec2add(PyObject *self, PyObject *args)
{

  PyObject * t1;
  PyObject * t2;

  PyArg_ParseTuple(args, "OO", &t1, &t2);

  Ec2 e1 = tup_Ec2(t1);
  Ec2 e2 = tup_Ec2(t2);


  return Ec2_tup(e1 + e2);
  
}

static PyObject *
ec2sub(PyObject *self, PyObject *args)
{

  PyObject * t1;
  PyObject * t2;

  PyArg_ParseTuple(args, "OO", &t1, &t2);

  Ec2 e1 = tup_Ec2(t1);
  Ec2 e2 = tup_Ec2(t2);

  return Ec2_tup(e1 - e2);
  
}

static PyObject *
ec2eq(PyObject *self, PyObject * args)
{
  PyObject * t1;
  PyObject * t2;

  PyArg_ParseTuple(args, "OO", &t1, &t2);

  Ec2 e1 = tup_Ec2(t1);
  Ec2 e2 = tup_Ec2(t2);

  if (e1 == e2){
    return Py_True;
  } else {
    return Py_False;
  }
  
}


// Pairing Operations

static PyObject *
pairing(PyObject*self, PyObject *args)
{

  PyObject * t1;
  PyObject * t2;

  PyArg_ParseTuple(args, "OO", &t1, &t2);

  Ec1 e1 = tup_Ec1(t1);
  Ec2 e2 = tup_Ec2(t2);

  Fp12 e;

  opt_atePairing(e, e2, e1);

  return Fp12_tup(e);
}


static PyObject *
ec12mul(PyObject *self, PyObject *args)
{
  PyObject * t1;
  PyObject * t2;

  PyArg_ParseTuple(args, "OO", &t1, &t2);


  Fp12 f1 = tup_Fp12(t1);
  Fp12 f2 = tup_Fp12(t2);
    

  return Fp12_tup(f1 * f2);
  
}

static PyObject *
ec12eq(PyObject *self, PyObject *args)
{
  PyObject * t1;
  PyObject * t2;

  PyArg_ParseTuple(args, "OO", &t1, &t2);

  Fp12 f1 = tup_Fp12(t1);
  Fp12 f2 = tup_Fp12(t2);

  if (f1 == f2){
    return Py_True;
  } else {
    return Py_False;
  }

}

  

// Binary Field Operations.
static PyObject * add(PyObject *self, PyObject *args){return _fbop(args, 'a');}
static PyObject * sub(PyObject *self, PyObject *args){return _fbop(args, 's');}
static PyObject * mul(PyObject *self, PyObject *args){return _fbop(args, 'm');}
static PyObject * div(PyObject *self, PyObject *args){return _fbop(args, 'd');}

// Unary Field Operations.
static PyObject * neg(PyObject *self, PyObject *args){return _fuop(args, 'n');}
static PyObject * inv(PyObject *self, PyObject *args){return _fuop(args, 'i');}

//Debugging

static PyObject *
debug(PyObject *self, PyObject *args)
{
  return Py_None;
}

static PyMethodDef Methods[] = {
  {"add",  add, METH_VARARGS, "Field Add."},
  {"sub",  sub, METH_VARARGS, "Field Sub."},
  {"mul",  mul, METH_VARARGS, "Field Mul."},
  {"div",  div, METH_VARARGS, "Field Div."},
  {"neg",  neg, METH_VARARGS, "Field Additive Inverse."},
  {"inv",  inv, METH_VARARGS, "Field Multiplicative Inverse."},
  {"get_g1",  get_g1, METH_VARARGS, "TODO"},
  {"ec1smul",  ec1smul, METH_VARARGS, "TODO"},
  {"ec1add",  ec1add, METH_VARARGS, "TODO"},
  {"ec1sub",  ec1sub, METH_VARARGS, "TODO"},
  {"ec1eq",  ec1eq, METH_VARARGS, "TODO"},
  {"get_g2",  get_g2, METH_VARARGS, "TODO"},
  {"ec2smul",  ec2smul, METH_VARARGS, "TODO"},
  {"ec2add",  ec2add, METH_VARARGS, "TODO"},
  {"ec2sub",  ec2sub, METH_VARARGS, "TODO"},
  {"ec2eq",  ec2eq, METH_VARARGS, "TODO"},
  {"pairing",  pairing, METH_VARARGS, "TODO"},
  {"ec12mul",  ec12mul, METH_VARARGS, "TODO"},
  {"ec12eq",  ec12eq, METH_VARARGS, "TODO"},
  {"setup",  setup, METH_VARARGS, "Setup Curve Library."},
  {"get_order",  get_order, METH_VARARGS, "TODO"},
  {"debug",  debug, METH_VARARGS, "TODO"},
  {NULL}
};

static struct PyModuleDef Module = {
  PyModuleDef_HEAD_INIT,
  "wrapper",
  NULL,
  -1,  
  Methods
};

PyMODINIT_FUNC
PyInit_wrapper(void)
{
  return PyModule_Create(&Module);
}

int
main(int argc, char *argv[])
{
  wchar_t *program = Py_DecodeLocale(argv[0], NULL);
  if (program == NULL) {
    fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
    exit(1);
  }

  PyImport_AppendInittab("wrapper", PyInit_wrapper);
  Py_SetProgramName(program);
  Py_Initialize();
  PyImport_ImportModule("wrapper");

  PyMem_RawFree(program);
  return 0;
}
*/

#ifdef CPP
int main(int argc, char *argv[]) {
  setup();
  GF* a = new_gf(2);
  GF* b = new_gf(3);
  GF* c = new_gf(0);

  std::cout << to_string(a) << std::endl;
  std::cout << to_string(b) << std::endl;
  std::cout << to_string(c) << std::endl;

  add(c, a, b);

  std::cout << to_string(c) << std::endl;
  delete_gf(a);
  delete_gf(b);
  delete_gf(c);
}
#endif // CPP

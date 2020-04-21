#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "bn.h"
#include "zm.h"
#include "test_point.hpp"

using namespace mie;
using namespace bn;



typedef ZmZ<Vuint, Vuint> GF;


// Global Generators
Ec1 g1;
Ec2 g2;

// Setup

static PyObject *
setup(PyObject *self, PyObject *args)
{

  // Create generators
  CurveParam cp = CurveFp254BNb;
  Param::init(cp);
  
  const Point& pt = selectPoint(cp);
  g1 = Ec1(pt.g1.a, pt.g1.b);
  g2 = Ec2(
	   Fp2(Fp(pt.g2.aa), Fp(pt.g2.ab)),
	   Fp2(Fp(pt.g2.ba), Fp(pt.g2.bb))
	   );


  return Py_None;
}


static PyObject *
get_order(PyObject *self, PyObject *args)
{
  return PyUnicode_FromString(Param::r.toString().c_str());

}

// More Debugging

template<class T, class S>
void verify(const char *msg, const T& a, const S& b)
{
  if (a == b) {
    printf("%s : ok\n", msg);
  } else {
    printf("%s : ng\n", msg);
    PUT(a);
    PUT(b);
  }
}

// Conversions


static const GF
str_GF(const char *aStr)
{

  const GF a(aStr);
  a.setModulo(Param::r);

  return a;
  
}

static const Ec1
tup_Ec1(PyObject *args)
{

  const char *p0Str;
  const char *p1Str;
  const char *p2Str;

  PyArg_ParseTuple(args, "sss", &p0Str, &p1Str, &p2Str);

  Fp p0(p0Str);
  Fp p1(p1Str);
  Fp p2(p2Str);

  return Ec1(p0, p1, p2);

}

static PyObject *
Ec1_tup(Ec1 e)
{
  PyObject *t = PyTuple_New(3);


  PyObject *p0 = PyUnicode_FromString(e.p[0].toString().c_str());
  PyObject *p1 = PyUnicode_FromString(e.p[1].toString().c_str());
  PyObject *p2 = PyUnicode_FromString(e.p[2].toString().c_str());
  

  PyTuple_SetItem(t, 0, p0);
  PyTuple_SetItem(t, 1, p1);
  PyTuple_SetItem(t, 2, p2);

  return t;
}

static const Ec2
tup_Ec2(PyObject *args)
{

  PyObject * tx;
  PyObject * ty;
  PyObject * tz;

  PyArg_ParseTuple(args, "OOO", &tx, &ty, &tz);

  char *x1Str;
  char *x2Str;
  char *y1Str;
  char *y2Str;
  char *z1Str;
  char *z2Str;
    

  PyArg_ParseTuple(tx, "ss", &x1Str, &x2Str);
  PyArg_ParseTuple(ty, "ss", &y1Str, &y2Str);
  PyArg_ParseTuple(tz, "ss", &z1Str, &z2Str);


  return Ec2(
	     Fp2(Fp(x1Str), Fp(x2Str)),
	     Fp2(Fp(y1Str), Fp(y2Str)),
	     Fp2(Fp(z1Str), Fp(z2Str))
	     );

}

static PyObject *
Ec2_tup(Ec2 e)
{
  PyObject *tx = PyTuple_New(2);
  PyObject *ty = PyTuple_New(2);
  PyObject *tz = PyTuple_New(2);

  PyObject *x1 = PyUnicode_FromString(e.p[0].a_.toString().c_str());
  PyObject *x2 = PyUnicode_FromString(e.p[0].b_.toString().c_str());

  PyObject *y1 = PyUnicode_FromString(e.p[1].a_.toString().c_str());
  PyObject *y2 = PyUnicode_FromString(e.p[1].b_.toString().c_str());

  PyObject *z1 = PyUnicode_FromString(e.p[2].a_.toString().c_str());
  PyObject *z2 = PyUnicode_FromString(e.p[2].b_.toString().c_str());

  PyTuple_SetItem(tx, 0, x1);
  PyTuple_SetItem(tx, 1, x2);

  PyTuple_SetItem(ty, 0, y1);
  PyTuple_SetItem(ty, 1, y2);

  PyTuple_SetItem(tz, 0, z1);
  PyTuple_SetItem(tz, 1, z2);

  PyObject *t = PyTuple_New(3);

  PyTuple_SetItem(t, 0, tx);
  PyTuple_SetItem(t, 1, ty);
  PyTuple_SetItem(t, 2, tz);


  return t;
  
}

static const Fp6
tup_Fp6(PyObject *args)
{

  PyObject *t1;
  PyObject *t2;
  PyObject *t3;

  PyArg_ParseTuple(args, "OOO", &t1, &t2, &t3);



  char *aaStr;
  char *abStr;
  char *baStr;
  char *bbStr;
  char *caStr;
  char *cbStr;


  PyArg_ParseTuple(t1, "ss", &aaStr, &abStr);
  PyArg_ParseTuple(t2, "ss", &baStr, &bbStr);
  PyArg_ParseTuple(t3, "ss", &caStr, &cbStr);



  return Fp6(
	     Fp2(Fp(aaStr), Fp(abStr)),
	     Fp2(Fp(baStr), Fp(bbStr)),
	     Fp2(Fp(caStr), Fp(cbStr))
	     );
  
}

static const Fp12
tup_Fp12(PyObject *args)
{
  
  PyObject *t1;
  PyObject *t2;

  PyArg_ParseTuple(args, "OO", &t1, &t2);

  Fp6 a = tup_Fp6(t1);
  Fp6 b = tup_Fp6(t2);

  return Fp12(a, b);
  
}

static PyObject *
Fp6_tup(Fp6 e)
{
  PyObject *t = PyTuple_New(3);

  PyObject *aa = PyUnicode_FromString(e.a_.a_.toString().c_str());

  
  PyObject *ab = PyUnicode_FromString(e.a_.b_.toString().c_str());
  PyObject *ba = PyUnicode_FromString(e.b_.a_.toString().c_str());
  PyObject *bb = PyUnicode_FromString(e.b_.b_.toString().c_str());
  PyObject *ca = PyUnicode_FromString(e.c_.a_.toString().c_str());
  PyObject *cb = PyUnicode_FromString(e.c_.b_.toString().c_str());

  PyObject *ta = PyTuple_New(2);
  PyObject *tb = PyTuple_New(2);
  PyObject *tc = PyTuple_New(2);

  PyTuple_SetItem(ta, 0, aa);
  PyTuple_SetItem(ta, 1, ab);
  PyTuple_SetItem(tb, 0, ba);
  PyTuple_SetItem(tb, 1, bb);
  PyTuple_SetItem(tc, 0, ca);
  PyTuple_SetItem(tc, 1, cb);

  PyTuple_SetItem(t, 0, ta);
  PyTuple_SetItem(t, 1, tb);
  PyTuple_SetItem(t, 2, tc);

  return t;
  
}

static PyObject *
Fp12_tup(Fp12 e)
{

  PyObject *t = PyTuple_New(2);

  PyObject *a = Fp6_tup(e.a_);

  PyObject *b = Fp6_tup(e.b_);

  PyTuple_SetItem(t, 0, a);
  PyTuple_SetItem(t, 1, b);

  return t;
  
}


static PyObject *
_fbop(PyObject *args, char s)
{

  const char *aStr;
  const char *bStr;
  PyArg_ParseTuple(args, "ss", &aStr, &bStr);

  const GF a = str_GF(aStr);
  const GF b = str_GF(bStr);

  GF c;
  c.setModulo(Param::r);

  switch (s)
    {
    case 'a':
      c = a + b;
      break;
    case 's':
      c = a - b;
      break;
    case 'm':
      c = a * b;
      break;
    case 'd':
      c = a / b;
      break;
    }

  //std::cout << c << std::endl;

  return PyUnicode_FromString(c.toString().c_str());

}

static PyObject *
_fuop(PyObject *args, char s)
{

  const char *aStr;
  PyArg_ParseTuple(args, "s", &aStr);

  const GF a(aStr);
  a.setModulo(Param::r);

  GF b;
  b.setModulo(Param::r);

  switch (s)
    {
    case 'n':
      b = -a;
      break;
    case 'i':
      GF::inv(b, a);
      break;
    }

  return PyUnicode_FromString(b.toString().c_str());

}

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

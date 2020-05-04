#include "gfeccore.h"
#include "bn.h"
#include "zm.h"
#include "test_point.hpp"

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


std::string get_order()
{
  //return PyUnicode_FromString(Param::r.toString().c_str());
  return Param::r.toString();

}


// GF Methods

GF* new_gf(const char * n) {
  GF* a = new GF(n); 
  a->setModulo(Param::r);
  return a;
}

void remove(GF* a) {
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
  GF::inv(*a, *b);
}

bool eq(GF *a, GF * b) {
  return *a == *b;
}

std::string to_string(GF* a) {
  return a->toString();
}

// EC1 Methods

Ec1 * new_ec1() {
  Ec1 * a = new Ec1();
  return a;
}

Ec1* new_ec1(const char * p0_str, const char * p1_str, const char * p2_str) {
  Fp p0(p0_str);
  Fp p1(p1_str);
  Fp p2(p2_str);

  Ec1 * a = new Ec1(p0, p1, p2);
  return a;
}

void remove(Ec1* a) {
  delete a;
}

Ec1* get_g1() {
  return g1;
}

void add(Ec1* a, Ec1* b, Ec1* c) {
  *a = *b + *c;
}

void sub(Ec1* a, Ec1*b, Ec1* c) {
  *a = *b - *c;
}

void smul(Ec1* a, Ec1* b, GF* c) {
  *a = (*b) * (*c);
}

bool eq(Ec1 *a, Ec1 * b) {
  return *a == *b;
}

void normalize(Ec1* a) {
  a->normalize();
}

std::string to_string(Ec1* a) {
  return (a->p[0].toString() + "," +
	  a->p[1].toString() + "," +
	  a->p[2].toString());
}

// EC2 Methods

Ec2 * new_ec2() {
  Ec2 * a = new Ec2();
  return a;
}

Ec2 * new_ec2(std::string p0a_str,
	      std::string p0b_str,
	      std::string p1a_str,
	      std::string p1b_str,
	      std::string p2a_str,
	      std::string p2b_str) {

  Ec2 * a = new Ec2 (Fp2(Fp(p0a_str), Fp(p0b_str)),
		     Fp2(Fp(p1a_str), Fp(p1b_str)),
		     Fp2(Fp(p2a_str), Fp(p2b_str)));
  
  return a;
}

void remove(Ec2* a) {
  delete a;
}

Ec2* get_g2() {
  return g2;
}

void add(Ec2* a, Ec2* b, Ec2* c) {
  *a = *b + *c;
}

void sub(Ec2* a, Ec2*b, Ec2* c) {
  *a = *b - *c;
}

void smul(Ec2* a, Ec2* b, GF* c) {
  *a = (*b) * (*c);
}

bool eq(Ec2 *a, Ec2 * b) {
  return *a == *b;
}

std::string to_string(Ec2* a) {
  return (a->p[0].a_.toString() + "," +
	  a->p[0].b_.toString() + "," +
	  a->p[1].a_.toString() + "," +
	  a->p[1].b_.toString() + "," +
	  a->p[2].a_.toString() + "," +
	  a->p[2].b_.toString());
	  
}

// EC12

Fp12 * new_fp12() {
  Fp12 * a = new Fp12();
  return a;
}

void remove(Fp12* a) {
  delete a;
}

void pairing(Fp12 * a, Ec1 * b, Ec2 * c) {
  opt_atePairing(*a, *c, *b);
}

void mul(Fp12 * a, Fp12 * b, Fp12 * c) {
  *a = (*b) * (*c);
}

bool eq(Fp12 * a, Fp12 * b) {
  return *a == *b;
}

#ifdef CPP
int main(int argc, char *argv[]) {
  setup();
  GF* a = new_gf("2");
  GF* b = new_gf("3");
  GF* c = new_gf("0");

  std::cout << to_string(a) << std::endl;

  std::cout << to_string(a) << std::endl;
  std::cout << to_string(b) << std::endl;
  std::cout << to_string(c) << std::endl;

  add(c, a, b);

  std::cout << to_string(c) << std::endl;
  remove(a);
  remove(b);
  remove(c);

  Ec1 * A = new_ec1();

  add(A, g1, g1);
  smul(A, g1, new_gf("2"));

  std::cout << to_string(A) << std::endl;

  
}
#endif // CPP

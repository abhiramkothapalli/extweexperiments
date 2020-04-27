#pragma once

#ifdef CPP
#include "bn.h"
#include "zm.h"
#include "test_point.hpp"

using namespace mie;
using namespace bn;

typedef ZmZ<Vuint, Vuint> GF;
#endif // CPP

// Setup
void setup();

std::string get_order();

// Galois Field

GF* new_gf(const char* n);

void free(GF* a);

void add(GF* a, GF* b, GF* c);

void sub(GF* a, GF* b, GF* c);

void mul(GF* a, GF* b, GF* c);

void div(GF* a, GF* b, GF* c);

void neg(GF* a, GF* b);

void inv(GF* a, GF* b);

bool eq(GF *a, GF * b);

std::string to_string(GF* a);

// EC1 Methods

Ec1* new_ec1();

void free(Ec1* a);

Ec1* get_g1();

void add(Ec1* a, Ec1* b, Ec1* c);

void sub(Ec1* a, Ec1*b, Ec1* c);

void smul(Ec1* a, Ec1* b, GF* c);

bool eq(Ec1 *a, Ec1 * b);

// EC2 Methods

Ec2* new_ec2();

void free(Ec2* a);

Ec2* get_g2();

void add(Ec2* a, Ec2* b, Ec2* c);

void sub(Ec2* a, Ec2*b, Ec2* c);

void smul(Ec2* a, Ec2* b, GF* c);

bool eq(Ec2 *a, Ec2 * b);

// EC12

Fp12 * new_fp12();

void free(Fp12* a);

void pairing(Fp12 * a, Ec1 * b, Ec2 * c);

void mul(Fp12 * a, Fp12 * b, Fp12 * c);

bool eq(Fp12 * a, Fp12 * b);

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

GF* new_gf(unsigned long long n);

void delete_gf(GF* a);

void add(GF* a, GF* b, GF* c);

void sub(GF* a, GF* b, GF* c);

void mul(GF* a, GF* b, GF* c);

void div(GF* a, GF* b, GF* c);

void neg(GF* a, GF* b);

void inv(GF* a, GF* b);

std::string to_string(GF* a);

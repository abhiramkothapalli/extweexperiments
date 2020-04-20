/*
  a tiny sample of optimal ate pairing
*/
#include "bn.h"
#include "test_point.hpp"
#include <stdlib.h>     /* srand, rand */
#include <stdio.h>     /* srand, rand */
#include <ctime>

static int errNum = 0;

template<class T, class S>
void verify(const char *msg, const T& a, const S& b)
{
  if (a == b) {
    printf("%s : ok\n", msg);
  } else {
    printf("%s : ng\n", msg);
    PUT(a);
    PUT(b);
    errNum++;
  }
}

void sample2(const bn::CurveParam& cp)
{
  using namespace bn;

  // Init library
  Param::init(cp);

  // Create generators
  const Point& pt = selectPoint(cp);
  const Ec2 g2(
	       Fp2(Fp(pt.g2.aa), Fp(pt.g2.ab)),
	       Fp2(Fp(pt.g2.ba), Fp(pt.g2.bb))
	       );
  const Ec1 g1(pt.g1.a, pt.g1.b);

  puts("order of group");
  PUT(Param::r);
  

  const char *aStr = "12345678901234599999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999";
  const char *bStr = "998752342342342342424242421";
  const mie::Vuint a(aStr);
  const mie::Vuint b(bStr);

  const mie::Vuint c = a % Param::r;

  PUT(c)

  // scalar-multiplication sample
  {
    const mie::Vuint c = a + b;
    Ec1 Pa = g1 * a;
    Ec1 Pb = g1 * b;
    Ec1 Pc = g1 * c;
    Ec1 out = Pa + Pb;

    verify("check g1 * c = g1 * a + g1 * b", Pc, out);

  }

  Fp12 e;

  // calc e : G2 x G1 -> G3 pairing
  opt_atePairing(e, g2, g1);
  PUT(e);

  Ec2 g2a = g2 * a;

  Fp12 ea1;
  opt_atePairing(ea1, g2a, g1);

  Fp12 ea2 = power(e, a); // ea2 = e^a
  verify("e(g2 * a, g1) = e(g2, g1)^a", ea1, ea2);

  Ec1 g1b = g1 * b;
  Fp12 eb1;
  opt_atePairing(eb1, g2, g1b);

  Fp12 eb2 = power(e, b); // eb2 = e^b
  verify("e(g2a, g1 * b) = e(g2, g1)^b", eb1, eb2);

  Ec1 q1 = g1 * 12345;

  Fp12 e1, e2;
  opt_atePairing(e1, g2, g1);
  opt_atePairing(e2, g2, q1);

  Ec1 q2 = g1 + q1;
  opt_atePairing(e, g2, q2);
  verify("e = e1 * e2", e, e1 * e2);
}

void multi(const bn::CurveParam& cp)
{
  using namespace bn;
  // init my library
  Param::init(cp);
  const Point& pt = selectPoint(cp);
  const Ec2 g2(
	       Fp2(Fp(pt.g2.aa), Fp(pt.g2.ab)),
	       Fp2(Fp(pt.g2.ba), Fp(pt.g2.bb))
	       );
  const Ec1 g1(pt.g1.a, pt.g1.b);
  const size_t N = 10;
  const int c = 234567;
  std::vector<Ec1> g1s;
  g1s.resize(N);

  for (size_t i = 0; i < N; i++) {
    Ec1::mul(g1s[i], g1, c + i);
    g1s[i] = g1 * (c + i);
    g1s[i].normalize();
  }
  std::vector<Fp6> Qcoeff;
  Fp2 precQ[3];
  bn::components::precomputeG2(Qcoeff, precQ, g2.p);
  for (size_t i = 0; i < N; i++) {
    Fp12 e1;
    bn::components::millerLoop(e1, Qcoeff, g1s[i].p);
    e1.final_exp();
    Fp12 e2;
    opt_atePairing(e2, g2, g1s[i]);
    if (e1 != e2) {
      printf("err multi %d\n", (int)i);
    }
  }
}

int main(int argc, char *argv[])
{

  bn::CurveParam cp = bn::CurveFp254BNb;

  sample2(cp);
  printf("errNum = %d\n", errNum);

  
}

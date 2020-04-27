import gfeccore

def main():
    gfeccore.setup()
    a = gfeccore.new_gf(2)
    b = gfeccore.new_gf(3)
    c = gfeccore.new_gf(0)
    
    print(gfeccore.to_string(a))
    print(gfeccore.to_string(b))
    print(gfeccore.to_string(c))

    gfeccore.add(c, a, b)
    
    print(gfeccore.to_string(c))

    gfeccore.free(a);
    gfeccore.free(b);
    gfeccore.free(c);

    # Ec1
    
    a = gfeccore.new_ec1()
    g1 = gfeccore.get_g1()

    gfeccore.add(a, g1, g1)

    b = gfeccore.new_ec1()
    d = gfeccore.new_gf(2)

    gfeccore.smul(b, g1, d)

    assert gfeccore.eq(a, b)

    gfeccore.free(a)
    gfeccore.free(b)

    # Ec2

    a = gfeccore.new_ec2()
    g2 = gfeccore.get_g2()

    gfeccore.add(a, g2, g2)

    b = gfeccore.new_ec2()
    d = gfeccore.new_gf(2)

    gfeccore.smul(b, g2, d)

    assert gfeccore.eq(a, b)

    gfeccore.free(a)
    gfeccore.free(b)

    

main()

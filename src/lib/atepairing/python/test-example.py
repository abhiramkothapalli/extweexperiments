import example

def main():
    example.setup()
    a = example.new_gf(2)
    b = example.new_gf(3)
    c = example.new_gf(0)
    
    print(example.to_string(a))
    print(example.to_string(b))
    print(example.to_string(c))

    example.add(c, a, b)
    
    print(example.to_string(c))

    example.delete_gf(a);
    example.delete_gf(b);
    example.delete_gf(c);


main()

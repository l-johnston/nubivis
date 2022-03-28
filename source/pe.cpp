#include <iostream>
#include <string>
#include "parser.h"

using namespace std;

int main(int32_t argc, char **argv)
{
    Parser p{};
    if (argc > 1)
    {
        for (int32_t i = 1; i < argc; i++)
            cout << p.parse(argv[i]) << endl;
    }
    else
    {
        string e;
        getline(cin, e);
        cout << p.parse(e) << endl;
    }
}

#include "vec3.h"
#include "triangle.h"
#include "mesh.h"
using namespace std;

int main()
{
    Mesh mesh1;
    mesh1.add(Vec3(0,0,0), Vec3(0,0,1), Vec3(0,1,0));

    mesh1.stl_write("test.stl");
    return 0;
}
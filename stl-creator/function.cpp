#include "vec3.h"
#include "mesh.h"

#define HEIGHT 101
#define WIDTH 101
#define PITCH 0.3
#define THICKNESS 3

// This function determines the shape
double func(double x, double y)
{
	double frequency = 4;
	double angular_frequency = 2 * 3.14 * frequency;
	double z = 2 * sin(x * angular_frequency) + 2 * sin(y * angular_frequency);
	return z;
}

int main()
{
	int x, y;
	double heightmap[HEIGHT][WIDTH];

	for (y = 0; y < HEIGHT; y++)
	{
		for (x = 0; x < WIDTH; x++)
		{
			heightmap[y][x] = func((double)x / WIDTH - 0.5, (double)y / HEIGHT - 0.5);
		}
	}

	Mesh mesh_function;

	for (y = 0; y < HEIGHT - 1; y++)
	{
		for (x = 0; x < WIDTH - 1; x++)
		{
			mesh_function += create_quadrilateral(
				Vec3((x + 0) * PITCH, (y + 0) * PITCH, heightmap[(y + 0)][(x + 0)]),
				Vec3((x + 0) * PITCH, (y + 1) * PITCH, heightmap[(y + 1)][(x + 0)]),
				Vec3((x + 1) * PITCH, (y + 1) * PITCH, heightmap[(y + 1)][(x + 1)]),
				Vec3((x + 1) * PITCH, (y + 0) * PITCH, heightmap[(y + 0)][(x + 1)]));
		}
	}

	mesh_function.translate(Vec3(-0.5 * WIDTH * PITCH, -0.5 * HEIGHT * PITCH, 0));

	mesh_function.stl_write("function.stl");
}

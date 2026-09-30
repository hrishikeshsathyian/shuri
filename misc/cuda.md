#### CUDA Programming Model - Introduction

The CUDA programming model is a programmer-facing abstraction used to describe parallel work on an Nvidia GPU. At a high level 
- Device = GPU
- Host = CPU 
- Kernel = function called by the host that then runs on the device 

```
__global__ void hello() {
    printf("Hello from the GPU!\n");
}

int main() {
    int blocks_per_grid = 1;
    int threads_per_block = 1;

    hello<<<blocks_per_grid, threads_per_block>>>();

    cudaDeviceSynchronize();

    return 0;
}
```

_ _ global _ _ prefix indicates that the function is a kernel. It must have a void return type, CANNOT access CPU memory directly and CANNOT have varargs.
**Needs to be called with execution configuration** <<blocks_per_grid, threads_per_block, shared_mem_size_per_block>>

_ _ device _ _ prefix for functions called within GPU code

_ _ host _ _ prefix used for CPU functions by default


#### CUDA Programming Model - Threads, Blocks and Grids 

CUDA threads are logically organised into blocks. Programmer specifies the number of threads per block. Each thread can have a 1D, 2D, 3D index within the block but this is purely for convenience. Each block is assigned to only one Streaming Multiprocessor (SM) for the entire kernel duration.






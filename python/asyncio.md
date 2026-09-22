## asyncio 


##### Table of Contents

1. [intro](#intro)
2. [async functions and coroutines](#async-functions-and-coroutines)
3. [the event loop and asyncio.run()](#the-event-loop-and-asyncio.run())
4. [running coroutines with `await`](#running-coroutines-with-await)
5. [actually achieving concurrency with asyncio](#actually-achieving-concurrency-with-asyncio)
6. [tasks](#tasks)
7. [when to use asyncio](#when-to-use-asyncio)
8. [other ways to create tasks](#other-ways-to-create-tasks)


### intro

asyncio is a built-in Python library used to write concurrent code. It runs on a single thread and uses a **single-threaded event loop** to achieve **cooperative** multi-tasking.  

> to refresh, concurrency is the structure and design of managing multiple tasks in overlapping time periods through interleaving, where parallelism is the actual physical execution of multiple tasks at the exact same time. 


### async functions and coroutines 

You define an async function (officially a *coroutine function*) by writing `async def` instead of `def`. The key difference is what happens when you call it: a regular function runs its body immediately, but an async function does not. Instead, it returns a *coroutine object*, a paused computation that hasn't started yet and is waiting for something to run it.

```python
def regular():
    print("hello")

async def asynchronous():
    print("hello")

regular()              # prints "hello"
c = asynchronous()     # prints nothing!
print(c)               # <coroutine object asynchronous at 0x...>
```

To actually run the coroutine, we need either 
- `await` from inside another async function OR 
- `asyncio.run()` from a regular, synchronous code chunk

### the event loop and asyncio.run()

As mentioned previously, async functions return a coroutine. Coroutines do not run themselves. They need something to start them, pause them and resume them. That is the **event loop**

The event loop: a scheduler, running on a single thread, manages coroutines and decides which one runs next. We call `asyncio.run()`, pass in a coroutine object and it
- creates a new event loop on the current thread
- runs the coroutine until it finishes 
- closes the loop and cleans up 
- returns the coroutine's result 

```python
import asyncio

async def greet():
    print("hello")
    return 42

result = asyncio.run(greet())   # prints "hello"
print(result)                   # 42
```

> Note that asyncio.run() takes the coroutine as the argument and not the function itself. 

>asyncio.run() is a blocking call; that line does not finish until the coroutine runs

### running coroutines with await 

Once you are inside a coroutine, you can only run other coroutines with `await`

> `asyncio.run()` calls cannot be nested. it always creates a *new* event loop, so calling it from inside a coroutine (where a loop is already running) raises a RuntimeError. Hence, we call 'asyncio.run()' at the top level, and use `await` within to run other coroutines 



```python
import asyncio

async def get_number():
    await asyncio.sleep(1)   # pretend this is a network call
    return 42

async def main():
    n = await get_number()   # main pauses until get_number finishes
    print(n)                 # 42

asyncio.run(main())
```

##### `await` pauses the coroutine, not the entire thread

This is the most important idea in asyncio. When a coroutine awaits something that isn't ready yet (like `asyncio.sleep` or a network response), it doesn't freeze the program. It steps aside and hands control back to the event loop, saying "wake me up when this is done."

The event loop is then free to run any *other* coroutine that's ready. In the example above there are no others, so the loop simply waits, and the result looks sequential. But `await` is what creates the *opportunity* for switching, and it's the only place switching can happen. In the next section, we see how we can schedule other coroutines on the same event loop and achieve concurrency.

### actually achieving concurrency with asyncio 

As seen in the previous section, awaiting coroutines one after the other is sequential. While `main` calls `get_number()` and pauses at `asyncio.sleep`, it hands control to the event loop but the event loop had nothing else to run. For concurrency, the event loop needs **multiple things** to juggle. When one is paused waiting, the loop switches to another that's ready. These are called Tasks. 

### tasks 

A **Task** is the unit of work the event loop schedules. Each Task is created with one coroutine and drives it to completion. Any coroutines that coroutine `await`s, run inside the same Task, as part of one chain. When anything in the chain has to wait, the whole Task pauses and hands over control to the event loop, which can then allow another Task to run.
> this is referred to as **cooperative scheduling**: A Task runs until it voluntarily gives up control at an `await`. This is in contract to preemptive scheduling, for example in certain OS multithreading, where the OS can pause a thread at any moment and swtich to another. 

```python
task = asyncio.create_task(some_coroutine())
```

| | `await coro()` | `asyncio.create_task(coro())` |
|---|---|---|
| Where does the coroutine run? | Inside the current Task, as part of its chain | In a new, separate Task |
| Current coroutine... | Pauses until it's finished | Keeps going immediately |
| Returns | The coroutine's result | A `Task` object |


### walkthrough example of tasks

``` python 
import asyncio

async def say(word, seconds):
    await asyncio.sleep(seconds) # at this sleep, the current running Task will hand over control
                                 # to the Event Loop and let another Task run
    print(word)

async def main():
    A = asyncio.create_task(say("slow", 2)) # create Task A, cannot run until the current Task gives up control of Event Loop, 
                                            # i.e when current main() Task hands control over at an await 
    B = asyncio.create_task(say("fast", 1)) # ^ same thing, Task created but cannot run until Event Loop schedules itn
    await A # since the value of Task A is not ready, the Task main() hands control to Event Loop, that schedules Task A to be run
    await B

asyncio.run(main())

```

##### output:
``` python 
Fast
Slow

# Total Time : 2 seconds, NOT 3 seconds => Why?
```

##### explanation
What is most important to understand here is that `await a` is not saying that only Task A can execute. It is just saying to wait for Task A's result before moving on to the next line. Task B can still run if the event loop schedules it. 
In this case when Task A runs into its `await asyncio.sleep()` it hands control to the event loop, allowing Task B to execute hence allowing for Task B's `fast` to be printed first.

This is why the runtime is 2 seconds instead of 3, because Task B concurrently runs while Task A is sleeping.

> **Which Task runs first when main Task hands control to Event Loop?** 

>When `main` hands control to the Event Loop, both
> `a` and `b` are ready. CPython runs ready Tasks in the order they were
> scheduled, so `a` starts first, but asyncio doesn't guarantee this.
> Don't write code that depends on Tasks starting in a particular order!!!!!!


### when to use asyncio

Because a Task can only give up control at an `await` on something that isn't ready yet, asyncio works well when your code spends most of its time
**waiting**, and badly when it spends most of its time **computing**.

**I/O-bound work (good fit).** Network calls, API requests, database queries, and file or socket operations all involve waiting for something outside your program. Each wait is an `await` where the Task hands control to the loop, so other Tasks can run in the meantime.

**CPU-bound work (bad fit).** Heavy calculations, image processing, and parsing huge files keep the CPU busy with no waiting involved. There's no `await` where the Task can step aside, so it holds the event loop until it's done, and every other Task freezes. You do not really gain much speedup from this, overhead of creating Tasks might instead slow down performance. 


### other ways to create tasks
`asyncio.create_task()` is the fundamental way to create a Task, but there are other higher-level tools that we should instead use. All of them wrap coroutines in Tasks and run them concurrently. They differ in **how results get back** and **what happens when a Task fails**.

The examples below use this coroutine:

```python
async def say(word, seconds):
    await asyncio.sleep(seconds)
    print(word)
    return word
```

### `asyncio.gather()`

Runs the coroutines concurrently, waits for **all** of them to finish, then returns their results as a list **in the order you passed them**, not the order they finished.

```python
results = await asyncio.gather(say("slow", 2), say("fast", 1))
# prints "fast", then "slow"
print(results)   # ['slow', 'fast']  (at 2s)
```

If one raises an exception, `gather` raises it, but the other Tasks **keep running** in the background.

### `asyncio.TaskGroup`

Tasks created inside the `async with` block are guaranteed to be finished when the block exits. If one fails, the rest are **cancelled**, so nothing is left running by accident.

```python
async with asyncio.TaskGroup() as tg:
    a = tg.create_task(say("slow", 2))
    b = tg.create_task(say("fast", 1))
# both are done here
print(a.result(), b.result())   # slow fast
```

### `asyncio.as_completed()`

Runs the coroutines concurrently and hands each result **as soon as it finishes**, fastest first. All the coroutines are wrapped in Tasks immediately; each item you iterate over is an awaitable for whichever Task finishes next.

```python
for next_done in asyncio.as_completed([say("slow", 2), say("fast", 1)]):
    result = await next_done
    print("got", result)
# got fast   (at 1s)
# got slow   (at 2s)
```
Because results arrive in finish order, you lose the link between each result and the input it came from. If you need that link, include it in thereturn value (e.g. return `(word, result)`).



# ProxyPool
## 描述
简易高效的代理池，提供如下功能：

- 存储模块使用 Redis 的有序集合，用以代理的去重和状态标识，同时它也是中心模块和基础模块，将其他模块串联起来。
- 获取模块定时从代理网站获取代理，将获取的代理传递给存储模块，保存到数据库。
- 检测模块定时通过存储模块获取所有代理，并对其进行检测，根据不同的检测结果对代理设置不同的标识。
- 接口模块通过 Web API 提供服务接口，其内部还是连接存储模块，获取可用的代理。

## 代码详解
acquisition_module.py: 获取模块。

- get_proxies() 方法，将所有以 crawl 开头的方法调用一遍，获取每个方法返回的代理并组合成列表形式返回。
- 将获取代理的方法统一定义以crawl开头
- 你可能会想知道是怎样获取了所有以 crawl 开头的方法名称的。其实这里借助于元类来实现，定义了一个 ProxyMetaclass，Crawl 类将它设置为元类，元类中实现了 new() 方法，这个方法有固定的几个参数，其中第四个参数 attrs 中包含了类的一些属性，这其中就包含了类中方法的一些信息，我们可以遍历 attrs 这个变量即可获取类的所有方法信息。所以在这里我们在 new() 方法中遍历了 attrs 的这个属性，就像遍历一个字典一样，键名对应的就是方法的名称，接下来判断其开头是否是 crawl，如果是，则将其加入到 CrawlFunc 属性中，这样我们就成功将所有以 crawl 开头的方法定义成了一个属性，就成功动态地获取到所有以 crawl 开头的方法列表了。

api.py: 接口模块。
- 基于Flask，以Web API的形式暴露可用代理。


db.py: 数据库类，实现分数的设置，代理的获取等等。
- init() 方法是初始化的方法，参数是 Redis 的连接信息，默认的连接信息已经定义为常量，在 init() 方法中初始化了一个 StrictRedis 的类，建立 Redis 连接。这样当 RedisClient 类初始化的时候就建立了 Redis 的连接。
- add () 方法向数据库添加代理并设置分数，默认的分数是 INITIAL_SCORE 也就是 10，返回结果是添加的结果。
- random () 方法是随机获取代理的方法，首先获取 100 分的代理，然后随机选择一个返回，如果不存在 100 分的代理，则按照排名来获取，选取前 100 名，然后随机选择一个返回，否则抛出异常。
- decrease () 方法是在代理检测无效的时候设置分数减 1 的方法，传入代理，然后将此代理的分数减 1，如果达到最低值，那么就删除。
- exists () 方法判断代理是否存在集合中
- max () 方法是将代理的分数设置为 MAX_SCORE，即 100，也就是当代理有效时的设置。
- count () 方法返回当前集合的元素个数。
- all () 方法返回所有的代理列表，供检测使用。

Getter.py: Getter 类就是获取器类。

- 变量 POOL_UPPER_THRESHOLD 表示代理池的最大数量
- is_over_threshold()方法判断代理池是否已经达到了容量阈值
- run()方法，首先判断了代理池是否达到阈值，然后在这里就调用了Crawler类的CrawlFunc属性，获取到所有以crawl开头的方法列表，依次通过get_proxies()方法调用，得到各个方法抓取到的代理，然后再利用RedisClient的add()方法加入数据库，这样获取模块的工作就完成了。

Scheduler.py: 调度模块。
- 调用以上所定义的三个模块，将以上三个模块通过多进程的形式运行起来

Tester.py: 检测模块.
- init()方法中建立了一个RedisClient对象，供类中其他方法使用。
- test_single_proxy()方法，用来检测单个代理的可用情况
- run()方法里面获取了所有的代理列表，使用Aiohttp分配任务，启动运行，这样就可以进行异步检测了，


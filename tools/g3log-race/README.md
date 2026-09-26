# g3log-race: the level-map race behind aifoundry3's host crashes, without a card

libetrt's thread-pool workers log at the custom g3log levels `VERBOSE_HIGH/MID/LOW`, which only
`logging::LoggerDefault` registers. When a host program never constructs it, the first `LOG(VLOG_MID)` from
several freshly started workers inserts the level into g3log's `std::map` of levels from all of them at once.
Four core dumps on aifoundry3 (25 Sep 2026) stop in exactly that insert (`g3::logLevel` →
`_Rb_tree_insert_and_rebalance`). This program reproduces the race on the host CPU alone.

    g++ -O2 -std=c++17 -I/opt/et/include race.cpp -o race -L/opt/et/lib -lg3log -Wl,-rpath,/opt/et/lib -pthread
    nice ./race 20000 4            # threads make the first call for an unregistered level together
    nice ./race 20000 4 register   # the level registered first, as the host programs now do

On aifoundry2 (25 Sep 2026, three runs each), 1,087, 1,358 and 1,412 of 20,000 trials without registration left
the map with the wrong number of levels; 0 of 60,000 with it. Every host program in `workloads/*/host/main.cpp`
calls `registerRuntimeLogLevels()` first in `main` since then. Binaries built before that (the version-3
campaign's) can still crash this way: about one launch in 100 on aifoundry3, none seen on aifoundry2.

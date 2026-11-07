// desk stub (E184 syntax check only): the g3log names main.cpp uses
#pragma once
struct LEVELS { LEVELS(int, const char*) {} };
namespace g3 { const int kDebugValue = 800; namespace only_change_at_initialization { inline void addLogLevel(LEVELS, bool) {} } }

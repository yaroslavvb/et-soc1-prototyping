// ccheck's mock build: the two g3log names workloads/sparsity/host/main.cpp uses.
#pragma once
struct LEVELS {
  int value;
  const char* text;
  LEVELS(int v, const char* t) : value(v), text(t) {}
};
namespace g3 {
constexpr int kDebugValue = 100;
namespace only_change_at_initialization {
inline void addLogLevel(LEVELS, bool) {}
}  // namespace only_change_at_initialization
}  // namespace g3

CXX      ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Wpedantic

LABS := 1 2 3 4 5 6 7

.PHONY: all clean $(LABS)

all: $(LABS)

define LAB_template
$(1): $(1)/lab
$(1)/lab: $(1)/main.cpp
	$$(CXX) $$(CXXFLAGS) $(1)/main.cpp -o $(1)/lab
endef

$(foreach lab,$(LABS),$(eval $(call LAB_template,$(lab))))

clean:
	@for d in $(LABS); do rm -f $$d/lab; done

SRC = ro.ofn
TMPDIR = .
ROBOT = robot

.PHONY: normalize_src
normalize_src: $(SRC)
	$(ROBOT) convert -i $< -f ofn -o $(TMPDIR)/normalise && mv $(TMPDIR)/normalise $<

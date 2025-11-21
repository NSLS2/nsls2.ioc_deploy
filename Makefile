update:
	$(eval TARGET := update)

delete:
	$(eval TARGET := delete)

role:
	@if [ -z "${TARGET}" ]; then \
		pixi run make-role; \
	else \
		pixi run $(TARGET)-role; \
	fi
	git status

module:
	@if [ -z "${TARGET}" ]; then \
		pixi run make-module \
	else \
		pixi run $(TARGET)-module; \
	fi
	git status

report:
	pixi run report

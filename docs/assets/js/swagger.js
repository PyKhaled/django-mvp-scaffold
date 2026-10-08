(function () {
  function initializeSwagger() {
    const container = document.getElementById("swagger-ui");
    if (!container || container.dataset.initialized === "true") return;

    if (typeof SwaggerUIBundle !== "function") {
      container.textContent =
        "Swagger UI could not load. Use the OpenAPI document linked above.";
      return;
    }

    container.dataset.initialized = "true";
    SwaggerUIBundle({
      url: new URL(container.dataset.specUrl, document.baseURI).href,
      domNode: container,
      deepLinking: true,
      presets: [SwaggerUIBundle.presets.apis],
      supportedSubmitMethods: [],
      validatorUrl: null,
      persistAuthorization: false
    });
  }

  // Material's stream also runs after instant navigation, when enabled.
  if (typeof document$ !== "undefined") {
    document$.subscribe(initializeSwagger);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeSwagger);
  } else {
    initializeSwagger();
  }
})();

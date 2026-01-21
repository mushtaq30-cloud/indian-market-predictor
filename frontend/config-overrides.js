module.exports = function override(config, env) {
  // Fix webpack dev server deprecated middleware options
  if (config.devServer) {
    // Remove deprecated onBeforeSetupMiddleware and onAfterSetupMiddleware
    delete config.devServer.onBeforeSetupMiddleware;
    delete config.devServer.onAfterSetupMiddleware;

    // Use setupMiddlewares instead
    config.devServer.setupMiddlewares = (middlewares, devServer) => {
      // Custom middleware can be added here if needed
      return middlewares;
    };
  }

  return config;
};

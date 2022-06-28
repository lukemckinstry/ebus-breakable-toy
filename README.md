# Electric Buses - A Breakable Toy

## Description

Collects municipal bus transit routes and facilitates anotation to show adoption of electric vehicles for passenger service 

## Getting Started

### Dependencies

* Docker

### Setup Development Environment

* Build containers 
```
.scripts/setup
```

### Executing Program

* Run containers 
```
./scripts/server
```
Open [http://localhost:9202](http://localhost:9202) to view it in the browser.

* Update development environment:
    * Run migrations
    * Create superuser
    * Collect static files
    * Gather sample GTFS data for testing purposes
```
./scripts/update
```

* Run tests

```
./scripts/tests
```

### STRTA

This project uses [`scripts-to-rule-them-all`](https://github.com/azavea/architecture/blob/master/doc/arch/adr-0000-scripts-to-rule-them-all.md) to bootstrap, test, and maintain projects consistently across all teams. Below is a quick explanation for the specific usage of each script.

| Script      | Use                                                        |
| ----------- | ---------------------------------------------------------- |
| `server`    | Start the application backend server                       |
| `setup`     | Setup the project development environment                  |
| `test`      | Run linters and tests                                      |
| `update`    | Update project, assemble, run migrations                   |
| `cipublish` | Build and publish image to AWS container registry          |
| `infra`     | Execute Terraform subcommands with remote state management |

### Deployment

Use `./scripts/cipublish` to build and publish container images for the project to AWS ECR. Use `python deploy/update_ecs/py --cluster app --service ebus_app` to update the task definition of the ECS service to use the latest published container image.
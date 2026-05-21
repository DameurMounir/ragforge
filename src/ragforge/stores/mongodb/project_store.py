from src.ragforge.models.db_schemes import Project
from src.ragforge.stores.mongodb.base_store import BaseMongoStore
from src.ragforge.stores.mongodb.collections import MongoCollection



class ProjectStore(BaseMongoStore):
    """
    MongoDB store for project records.
    """

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[MongoCollection.PROJECTS.value]

    async def create_project(self, project: Project) -> Project:
        """
        Insert a new project record.
        """
        result = await self.collection.insert_one(
            project.model_dump(by_alias=True, exclude_unset=True)
        )
        project.id = result.inserted_id

        return project

    async def get_project_by_id(self, project_id: str) -> Project | None:
        """
        Return a project by its public project_id.
        """
        record = await self.collection.find_one({'project_id': project_id})

        if record is None:
            return None

        return Project(**record)

    async def get_project_or_create_one(self, project_id: str) -> Project:
        """
        Return an existing project or create it if missing.
        """
        project = await self.get_project_by_id(project_id=project_id)

        if project is not None:
            return project

        project = Project(project_id=project_id)
        return await self.create_project(project=project)

    async def get_all_projects(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Project], int]:
        """
        Return paginated projects and total number of pages.
        """
        total_documents = await self.collection.count_documents({})

        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1

        cursor = (
            self.collection
            .find()
            .skip((page - 1) * page_size)
            .limit(page_size)
        )

        projects = []

        async for record in cursor:
            projects.append(Project(**record))

        return projects, total_pages

    
    @classmethod
    async def create_instance(cls, db_client: object):
        """
        Create store instance and initialize collection indexes./Branch 11
        """
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self) -> None:
        """
        Initialize MongoDB indexes for the projects collection.
        """
        for index in Project.get_indexes():
            await self.collection.create_index(
                index['key'],
                name=index['name'],
                unique=index['unique'],
            )
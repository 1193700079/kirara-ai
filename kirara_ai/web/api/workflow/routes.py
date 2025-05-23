import os
from typing import List

from quart import Blueprint, g, jsonify, request

from kirara_ai.workflow.core.block.registry import BlockRegistry
from kirara_ai.workflow.core.workflow import WorkflowRegistry
from kirara_ai.workflow.core.workflow.builder import WorkflowBuilder

from ...auth.middleware import require_auth
from .models import BlockInstance, Wire, WorkflowDefinition, WorkflowInfo, WorkflowList, WorkflowResponse

workflow_bp = Blueprint("workflow", __name__)


@workflow_bp.route("", methods=["GET"])
@require_auth
async def list_workflows():
    """获取所有工作流列表"""
    registry: WorkflowRegistry = g.container.resolve(WorkflowRegistry)

    workflows = []
    for workflow_id, builder in registry._workflows.items():
        # 从 workflow_id 解析 group_id
        group_id, wf_id = workflow_id.split(":", 1)

        workflows.append(
            WorkflowInfo(
                group_id=group_id,
                workflow_id=wf_id,
                name=builder.name,
                description=builder.description,
                block_count=len(builder.nodes_by_name),
                metadata=getattr(builder, "metadata", None),
            )
        )
    workflows.sort(key=lambda x: f"{x.group_id}:{x.workflow_id}")
    return WorkflowList(workflows=workflows).model_dump()


@workflow_bp.route("/<group_id>/<workflow_id>", methods=["GET"])
@require_auth
async def get_workflow(group_id: str, workflow_id: str):
    """获取特定工作流的详细信息"""
    registry: WorkflowRegistry = g.container.resolve(WorkflowRegistry)
    block_registry: BlockRegistry = g.container.resolve(BlockRegistry)
    full_id = f"{group_id}:{workflow_id}"
    builder = registry.get(full_id)
    if not builder:
        return jsonify({"error": "Workflow not found"}), 404

    assert isinstance(builder, WorkflowBuilder)

    # 构建工作流定义
    blocks: List[BlockInstance] = []
    for node in builder.nodes:
        blocks.append(
            BlockInstance(
                type_name=block_registry.get_block_type_name(node.spec.block_class),
                name=node.name,
                config=node.spec.kwargs,
                position=node.position or {"x": 0, "y": 0},
            )
        )

    wires: List[Wire] = []
    for source_name, source_output, target_name, target_input in builder.wire_specs:
        wires.append(
            Wire(
                source_block=source_name,
                source_output=source_output,
                target_block=target_name,
                target_input=target_input,
            )
        )

    workflow_def = WorkflowDefinition(
        group_id=group_id,
        workflow_id=workflow_id,
        name=builder.name,
        description=builder.description,
        blocks=blocks,
        wires=wires,
        metadata=getattr(builder, "metadata", None),
    )

    return WorkflowResponse(workflow=workflow_def).model_dump()


@workflow_bp.route("/<group_id>/<workflow_id>", methods=["POST"])
@require_auth
async def create_workflow(group_id: str, workflow_id: str):
    """创建新的工作流"""
    data = await request.get_json()
    workflow_def = WorkflowDefinition(**data)

    registry: WorkflowRegistry = g.container.resolve(WorkflowRegistry)
    block_registry: BlockRegistry = g.container.resolve(BlockRegistry)

    # 检查工作流是否已存在
    full_id = f"{group_id}:{workflow_id}"
    if registry.get(full_id):
        return jsonify({"error": "Workflow already exists"}), 400

    # 创建工作流构建器
    try:
        # 创建工作流构建器
        builder = WorkflowBuilder(workflow_def.name)
        builder.description = workflow_def.description

        # 根据定义添加块和连接
        for block_def in workflow_def.blocks:
            block_class = block_registry.get(block_def.type_name)
            if not block_class:
                raise ValueError(f"Block type {block_def.type_name} not found")

            if not builder.head:
                builder.use(block_class, name=block_def.name, **block_def.config)
            else:
                builder.chain(block_class, name=block_def.name, **block_def.config)

            builder.update_position(block_def.name, block_def.position)
        
        # 不要用自动连线，用我们的
        builder.wire_specs = []
        # 添加连接
        for wire in workflow_def.wires:
            builder.force_connect(
                wire.source_block,
                wire.target_block,
                wire.source_output,
                wire.target_input
            )

        # 保存工作流
        file_path = registry.get_workflow_path(group_id, workflow_id)
        builder.save_to_yaml(file_path, g.container)

        # 注册工作流
        registry.register(group_id, workflow_id, builder)

        return workflow_def.model_dump()
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@workflow_bp.route("/<group_id>/<workflow_id>", methods=["PUT"])
@require_auth
async def update_workflow(group_id: str, workflow_id: str):
    """更新现有工作流"""
    data = await request.get_json()
    workflow_def = WorkflowDefinition(**data)

    registry: WorkflowRegistry = g.container.resolve(WorkflowRegistry)
    block_registry: BlockRegistry = g.container.resolve(BlockRegistry)

    # 检查工作流是否存在
    full_id = f"{group_id}:{workflow_id}"
    if not registry.get(full_id):
        return jsonify({"error": "Workflow not found"}), 404

    # 更新工作流
    try:
        # 创建新的工作流构建器
        builder = WorkflowBuilder(workflow_def.name)
        builder.description = workflow_def.description

        # 根据定义添加块和连接
        for block_def in workflow_def.blocks:
            block_class = block_registry.get(block_def.type_name)
            if not block_class:
                raise ValueError(f"Block type {block_def.type_name} not found")

            if not builder.head:
                builder.use(block_class, name=block_def.name, **block_def.config)
            else:
                builder.chain(block_class, name=block_def.name, **block_def.config)

            builder.update_position(block_def.name, block_def.position)
        
        # 不要用自动连线，用我们的
        builder.wire_specs = []

        # 添加连接
        for wire in workflow_def.wires:
            builder.force_connect(
                wire.source_block,
                wire.target_block,
                wire.source_output,
                wire.target_input
            )

        # 保存工作流
        file_path = registry.get_workflow_path(group_id, workflow_id)
        if os.path.exists(file_path):
            os.remove(file_path)
        new_file_path = registry.get_workflow_path(
            data["group_id"], data["workflow_id"]
        )
        builder.save_to_yaml(new_file_path, g.container)

        # 更新注册表
        registry.unregister(group_id, workflow_id)
        registry.register(data["group_id"], data["workflow_id"], builder)

        return workflow_def.model_dump()
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@workflow_bp.route("/<group_id>/<workflow_id>", methods=["DELETE"])
@require_auth
async def delete_workflow(group_id: str, workflow_id: str):
    """删除工作流"""
    registry: WorkflowRegistry = g.container.resolve(WorkflowRegistry)

    # 检查工作流是否存在
    full_id = f"{group_id}:{workflow_id}"
    if not registry.get(full_id):
        return jsonify({"error": "Workflow not found"}), 404

    try:
        # 从注册表中移除
        registry._workflows.pop(full_id, None)

        # 删除文件
        file_path = registry.get_workflow_path(group_id, workflow_id)
        if os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({"message": "Workflow deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

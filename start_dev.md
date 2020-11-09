# 第一次开发，执行命令序列

## 1. 该条命令只需操作一次，记录上游代码位置
`git remote add wb https://github.com/albertofwb/security-check-tool.git`

## 2. 获取远程最新 develop 分支代码
`git fetch wb develop`

## 3. 请不要直接在 develop 分支上开发，而是基于 develop 分支在自己的分支开发
`git checkout -b branch_name wb/develop`




# 第二次以及之后的所有新开发任务，操作步骤

## 1. 获取远程最新 develop 分支代码
`git fetch wb develop`

## 2. 创建自己的开发分支
`git checkout -b branch_name wb/develop`


# 分支命名

- 分支以任务类型前缀命名
    - 新特性   feature
    - 改 bug   fix
    - 重构     refactor
  


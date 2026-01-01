<template>
  <el-table :data="list" style="width: 100%;padding-top: 15px;">
    <!-- 订单号列 -->
    <el-table-column label="订单号" min-width="200">
      <template slot-scope="scope">
        {{ scope.row.order_no | orderNoFilter }}
      </template>
    </el-table-column>
    <!-- 金额列 -->
    <el-table-column label="金额" width="195" align="center">
      <template slot-scope="scope">
        ¥{{ scope.row.price | toThousandFilter }}
      </template>
    </el-table-column>
    <!-- 状态列 -->
    <el-table-column label="状态" width="100" align="center">
      <template slot-scope="{row}">
        <el-tag :type="row.status | statusFilter">
          {{ row.status | statusTextFilter }}
        </el-tag>
      </template>
    </el-table-column>
  </el-table>
</template>

<script>
import { transactionList } from '@/api/remote-search'

export default {
  filters: {
    // 过滤器：根据状态返回不同的Element UI标签类型（颜色）
    statusFilter(status) {
      const statusMap = {
        success: 'success', // 成功 -> 绿色
        pending: 'danger'   // 处理中 -> 红色
      }
      return statusMap[status]
    },
    // 过滤器：将英文状态翻译为中文
    statusTextFilter(status) {
      const statusMap = {
        success: '成功',
        pending: '处理中'
      }
      return statusMap[status]
    },
    // 过滤器：截断订单号字符串
    orderNoFilter(str) {
      return str.substring(0, 30)
    }
  },
  data() {
    return {
      list: null
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    // 获取交易列表数据
    fetchData() {
      transactionList().then(response => {
        // 仅显示前8条数据
        this.list = response.data.items.slice(0, 8)
      })
    }
  }
}
</script>
